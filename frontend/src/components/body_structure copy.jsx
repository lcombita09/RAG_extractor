import React, { useState, useEffect, useRef } from 'react';
import './styles/components.css';
import FileUploader from './uploadfile.jsx';
import Chatbot from './chatbot.jsx';
import * as XLSX from 'xlsx';
import Modal from 'react-modal';


Modal.setAppElement('#root'); // Ensure to set the root element for accessibility

const Body = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [selectedSummary, setSelectedSummary] = useState(null);
    const [previousSummary, setPreviousSummary] = useState(null);
    const [generatedSummaries, setGeneratedSummaries] = useState(() => {
        const savedSummaries = localStorage.getItem('generatedSummaries');
        return savedSummaries 
            ? JSON.parse(savedSummaries).map(summary => ({
                ...summary,
                conversations: summary.conversations || []
              }))
            : [];
    });

    // Conversations Chatbot
    const [isExecuting, setIsExecuting] = useState(false);
    const [selectedTenderName, setSelectedTenderName] = useState('Select tender');
    const [selectedConversation, setSelectedConversation] = useState({
        id: null, 
        fullConversation: [],
        nameConversation: "",
    });
    const [visibleConversations, setVisibleConversations] = useState({});

     // Buttons visualize, edit name, donwload and delete
     const [isVisualizeModalOpen, setIsVisualizeModalOpen] = useState(false);

    // Button Validation
    const [isLlmExecuting, setIsLlmExecuting] = useState(false);
    const [isValidateModalOpen, setIsValidateModalOpen] = useState(false);
    const [incorrectAnswers, setIncorrectAnswers] = useState(null);
    const [selectedIncorrectAnswer, setSelectedIncorrectAnswer] = useState('No selection');
    const [selectedSolution, setSelectedSolution] = useState('No solution selected');
    const [isDropdownVisible, setIsDropdownVisible] = useState(false);
    const [isSolutionVisible, setIsSolutionVisible] = useState(false);
    const [inputExpert, setInputExpert] = useState('');
    const [inputPrompt, setInputPrompt] = useState('');
    const [inputLlm, setInputLlm] = useState('');

    // Ref for dropdown menu
    const dropdownRef = useRef(null);

    useEffect(() => {
        localStorage.setItem('generatedSummaries', JSON.stringify(generatedSummaries));
    }, [generatedSummaries]);

    // Close the dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsDropdownVisible(false);
                setIsSolutionVisible(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);


    // Buttons visualize, edit name, donwload and delete
    const handleVisualize = (summary) => {
        setPreviousSummary(summary);
        setIsVisualizeModalOpen(true);
    };
    
    const closeVisualizeModal = () => {
        setIsVisualizeModalOpen(false);
    };
    
    const handleEditName = (summary) => {
        const oldName = summary.editableName;
        const newName = prompt('Enter new name for the file:', summary.editableName);
        if (newName) {
            const nameExists = generatedSummaries.some(
                (summary) => summary.editableName === newName
            );
            if (nameExists) {
                alert('Two summaries can not have the same name.');
                return;
            }
            setGeneratedSummaries(prevSummaries => 
                prevSummaries.map(summary => 
                    summary.editableName === oldName
                        ? { ...summary, editableName: newName }
                        : summary
                )
            );
        }
    };

    const handleDownload = (name, data) => {
        if (data.length === 0) return;
    
        const ws = XLSX.utils.aoa_to_sheet([['Variable', 'Value', 'Validation state'], ...data]);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Sheet1");
        const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
        const blob = new Blob([wbout], { type: 'application/octet-stream' });
    
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = name.endsWith('.xlsx') ? name : name + '.xlsx';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const handleDelete = async (summary) => {
        const removingTableName = summary.editableName;
        const uploadFileName = summary.uploadFileName;
    
        const isConfirmed = window.confirm(`Are you sure you want to delete ${removingTableName} and all its conversations?`);

        if (isConfirmed) {
            // Send HTTP POST request to delete the vectorstore
            try {
                const response = await fetch('http://127.0.0.1:8000/delete-vectorstore', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ vectorstore_name: uploadFileName }),
                });
    
                if (!response.ok) {
                    throw new Error('Failed to delete vectorstore');
                }
    
                const result = await response.json();
    
                if (result.status === 'success') {
                    const existingConversation = summary.conversations.find(conversation => conversation === selectedConversation);
                    if (existingConversation){
                        setSelectedConversation({
                            id: null, 
                            fullConversation: [],
                            nameConversation: "",
                        });
                        setSelectedTenderName('Select Tender');
                    }
                    setGeneratedSummaries(prevSummaries =>
                        prevSummaries.filter(summary => summary.editableName !== removingTableName)
                    );
                    alert(result.message);
                } else {
                    alert(result.message);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while deleting the vectorstore');
            }
        }
    };

const handleEvaluation = async () => {
    setIsLoading(true);

    try {
        const response = await fetch('http://127.0.0.1:8000/get_evaluation', {
            method: 'POST',
        });

        if (!response.ok) {
            throw new Error('An error occurred during evaluation');
        }

        const jsonResponse = await response.json();
        console.log("Evaluation result:", jsonResponse);

    } catch (error) {
        console.error("Error:", error);
    } finally {
        setIsLoading(false);
    }
};


    // Validation button
    const handleValidate = (summary) => {
        setSelectedSummary(summary);
        setPreviousSummary(summary);
        setIsValidateModalOpen(true);
    };
    
    const changeValidationState = (rowIndex, newState) => {
        setSelectedSummary(prevSummary => {
            const updatedTableData = [...prevSummary.tableData];
            updatedTableData[rowIndex] = [
                updatedTableData[rowIndex][0],
                updatedTableData[rowIndex][1],
                newState
            ];
    
            const updatedSummary = { ...prevSummary, tableData: updatedTableData };
    
            const incorrectEntries = updatedSummary.tableData
                .filter(([key, value, validationState]) => validationState === 'Negative')
                .map(([key]) => key);
    
            setIncorrectAnswers(incorrectEntries);
            setSelectedIncorrectAnswer('No selection');
    
            return updatedSummary;
        });
    };
    
    
    const saveValidationChanges = () => {
        if (JSON.stringify(previousSummary) === JSON.stringify(selectedSummary)) {
            alert('No change has been changed');
            return;
        }
        setGeneratedSummaries(prevSummaries => {
            const updatedSummaries = prevSummaries.map(summaryObject => 
                summaryObject === previousSummary 
                    ? { ...selectedSummary, validation: true } 
                    : summaryObject
            );
            return updatedSummaries;
        });        
        setPreviousSummary(selectedSummary);
        correctWrongAnswers;
    };

    const correctWrongAnswers = () => {
        const incorrectEntries = selectedSummary.tableData
            .filter(([key, value, validationState]) => validationState === 'Negative')
            .map(([key]) => key);
    
        const nonDefinedEntries = selectedSummary.tableData.filter(
            ([key, value, validationState]) => validationState === 'None'
        );
    
        if (nonDefinedEntries.length > 0) {
            alert("Value every response in the Validation column!");
        } 
    
        setIncorrectAnswers(incorrectEntries);
    };

    const handleInputExpertChange = (e) => {
        setInputExpert(e.target.value);
    };

    const handleInputPromptChange = (event) => {
        setInputPrompt(event.target.value);
    }

    const handleInputLlmChange = (event) => {
        setInputLlm(event.target.value);
    }

    const handleExpertSubmit = (e) => {
        e.preventDefault();
        if (inputExpert.trim()) {
            setSelectedSummary(prevSummary => {
                const updatedTableData = prevSummary.tableData.map(row => 
                    row[0] === selectedIncorrectAnswer
                    ? [row[0],
                        inputExpert,
                        'Positive']
                    : row
                );
                const updatedSummary = { ...prevSummary, tableData: updatedTableData };

                const incorrectEntries = updatedSummary.tableData
                .filter(([key, value, validationState]) => validationState === 'Negative')
                .map(([key]) => key);
    
                setIncorrectAnswers(incorrectEntries);
                setSelectedIncorrectAnswer('No selection');
                setSelectedSolution('No selection');
                setInputExpert('');
                return updatedSummary;
            });
        }
    }

    const handleLlmSubmit = async (event) => {
        event.preventDefault();
        
        setIsLlmExecuting(true);
    
        try {
            // Make the POST request to the backend
            const response = await fetch('http://127.0.0.1:8000/validator', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    vectorstore_name: selectedSummary.uploadFileName,
                    input_prompt: inputPrompt,
                    input_llm: inputLlm,
                })
            });
    
            let textResponse = await response.text(); // Change const to let to allow reassignment

            // Remove quotes if the text comes between quotes
            if (textResponse.startsWith('"') && textResponse.endsWith('"')) {
                textResponse = textResponse.slice(1, -1);
            }
    
            if (textResponse.trim()) {
                setSelectedSummary(prevSummary => {
                    const updatedTableData = prevSummary.tableData.map(row => 
                        row[0] === selectedIncorrectAnswer
                        ? [row[0], textResponse, 'Positive']
                        : row
                    );
                    const updatedSummary = { ...prevSummary, tableData: updatedTableData };

                    const incorrectEntries = updatedSummary.tableData
                    .filter(([key, value, validationState]) => validationState === 'Negative')
                    .map(([key]) => key);
        
                    setIncorrectAnswers(incorrectEntries);
                    setSelectedIncorrectAnswer('No selection');
                    setSelectedSolution('No selection');
                    setInputPrompt('');
                    setInputLlm('');
                    return updatedSummary;
                });
            }
    
            setIsLlmExecuting(false);
        } catch (error) {
            console.error('Error during LLM submission:', error);
            setIsLlmExecuting(false);
        }
    };
    
    const closeValidateModal = () => {
        if (JSON.stringify(previousSummary) !== JSON.stringify(selectedSummary)) {
            const userConfirmed = window.confirm('You have unsaved changes. Are you sure you want to close without saving?');
            if (userConfirmed) {
                setIsValidateModalOpen(false);
                setIncorrectAnswers(null);
                setSelectedIncorrectAnswer('No selection');
                setSelectedSolution('No selection');
            }
        } else {
            setIsValidateModalOpen(false);
            setIncorrectAnswers(null);
            setSelectedIncorrectAnswer('No selection');
            setSelectedSolution('No selection');
        }
    };


    // Conversation and chatbot buttons
    const addNewConversation = (summary) => {
        const selSummary = summary;
        setSelectedTenderName(selSummary.editableName);

        const existingConversation = selSummary.conversations.find(conversation => conversation.nameConversation === "New conversation");
    
        if (existingConversation) {
            setSelectedConversation(existingConversation);
        } else {
            const newConversation = {
                id: Date.now(), 
                fullConversation: [],
                nameConversation: "New conversation",
            };
            setGeneratedSummaries(prevSummaries =>
                prevSummaries.map(summary =>
                    summary === selSummary
                        ? {
                              ...summary,
                              conversations: [...summary.conversations, newConversation]
                          }
                        : summary
                )
            );
            setSelectedConversation(newConversation);
        }
    };   

    const toggleConversationVisibility = (index) => {
        setVisibleConversations((prevState) => ({
            ...prevState,
            [index]: !prevState[index],
        }));
    };

    const handleSelectConversationAndTenderName = (summary, conversation) => {
        setSelectedTenderName(summary.editableName);
        setSelectedConversation(conversation);
    };
    
    const handleEditConversationName = (summary, conversation) => {
        const selSummary = summary;
        const selConversation = conversation;
        const newName = prompt('Enter new conversation name:', conversation.nameConversation || conversation.fullConversation[0]);
        
        if (newName) {
            setGeneratedSummaries(prevSummaries =>
                prevSummaries.map(summary =>
                    summary === selSummary
                        ? {
                              ...summary,
                              conversations: summary.conversations.map(conversation =>
                                  conversation.id === selConversation.id
                                      ? { ...conversation, nameConversation: newName }
                                      : conversation
                              )
                          }
                        : summary
                )
            );
        }
    };

    const handleDeleteConversation = (summary, conversation) => {
        const selSummary = summary;
        const selConversation = conversation;
    
        const updatedSummary = {
            ...selSummary,
            conversations: selSummary.conversations.filter(conversation => conversation.id !== selConversation.id)
        };
    
        setGeneratedSummaries(prevSummaries => 
            prevSummaries.map(summary => 
                summary === selSummary ? updatedSummary : summary
            )
        );

        if (selConversation === selectedConversation) {
            setSelectedConversation({
                id: null, 
                fullConversation: [],
                nameConversation: "",
            });
            setSelectedTenderName('Select Tender')
        }
    };    

    return (
        <div className="body" style={{ pointerEvents: isLoading | isExecuting | isLlmExecuting ? 'none' : 'auto',}}>
            <div className="left-hand-side">
                <div className="tender-title">
                    <h3>Tender summaries</h3>
                </div>
                <div className='tenders'>
                    {generatedSummaries.filter(summary => summary.validation === false).map((summary, index) => (
                        <div key={index} className="generated-summary">
                            <div style={{ display: 'flex', alignItems: 'center' }}>
                                <button 
                                    onClick={() => handleValidate(summary)} 
                                    style={{ 
                                    fontSize: '16px',
                                    marginRight: '10px', 
                                    background: '#F5F5F5', 
                                    border: '1px solid #1c59b5',
                                    borderRadius: '3px',
                                    padding: '5px',
                                    cursor: 'pointer' 
                                    }} 
                                    title= "Validate summary"
                                >
                                &#x1F4BB;
                                </button>

                                <Modal
                                    isOpen={isValidateModalOpen}
                                    onRequestClose={closeValidateModal}
                                    contentLabel="Excel Visualization"
                                    style={{
                                        overlay: { backgroundColor: 'rgba(0,0,0,0.5)' },
                                        content: { 
                                            maxWidth: '90vw', 
                                            maxHeight: '90vh', 
                                            margin: 'auto',
                                            overflow: 'auto' 
                                        }
                                    }}
                                >
                                    {selectedSummary && (
                                        <>
                                            <h2>Summary Table Validation</h2>
                                            <button onClick={closeValidateModal} style={{ marginBottom: '20px', border: '1px solid #1c59b5' }}>
                                                Close
                                            </button>
                                            <button onClick={() => saveValidationChanges()} style={{ marginBottom: '20px', marginLeft: '20px', border: '1px solid #1c59b5' }}>
                                                Save changes
                                            </button>
                                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                                <thead>
                                                    <tr>
                                                        <th style={{ border: '1px solid #1c59b5', padding: '8px' }}>Variable</th>
                                                        <th style={{ border: '1px solid #1c59b5', padding: '8px' }}>Value</th>
                                                        <th style={{ border: '1px solid #1c59b5', padding: '8px' }}>Validation</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {selectedSummary.tableData.map(([key, value, validationState], rowIndex) => (
                                                        <tr key={rowIndex}>
                                                            <td style={{ border: '1px solid #1c59b5', padding: '8px' }}>{key}</td>
                                                            <td style={{ border: '1px solid #1c59b5', padding: '8px' }}>{value}</td>
                                                            <td style={{ alignItems: 'center', justifyContent: 'space-between', border: '1px solid #1c59b5', padding: '8px' }}>
                                                                <button
                                                                    style={{ marginRight: '10px', cursor: 'pointer', border: '1px solid #1c59b5', backgroundColor: validationState === 'Positive' ? '#1c59b5' : 'transparent',
                                                                        color: validationState === 'Positive' ? 'white' : '#1c59b5'}}
                                                                    onClick={() => changeValidationState(rowIndex, 'Positive')}
                                                                >
                                                                    ✔️
                                                                </button>
                                                                <button
                                                                    style={{ cursor: 'pointer', border: '1px solid #1c59b5', backgroundColor: validationState === 'Negative' ? '#1c59b5' : 'transparent',
                                                                        color: validationState === 'Negative' ? 'white' : '#1c59b5' }}
                                                                    onClick={() => changeValidationState(rowIndex, 'Negative')}
                                                                >
                                                                    ❌
                                                                </button>
                                                            </td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </>
                                    )}
                                </Modal>
                            </div>
                            <p 
                            style={{ 
                                flexGrow: 1, 
                                whiteSpace: 'nowrap', 
                                overflow: 'hidden', 
                                textOverflow: 'ellipsis', 
                                margin: 0 
                            }} 
                            title={summary.editableName}
                            >
                            {summary.editableName}
                            </p>
                        
                            <div style={{ display: 'flex', alignItems: 'center' }}>
                                <button 
                                    onClick={() => handleVisualize(summary)} 
                                    style={{ 
                                    fontSize: '16px',
                                    marginRight: '10px', 
                                    background: '#F5F5F5', 
                                    border: '1px solid #1c59b5',
                                    borderRadius: '3px',
                                    padding: '5px',
                                    cursor: 'pointer' 
                                    }} 
                                    title="Visualize"
                                >
                                    &#128065;
                                </button>

                                <Modal
                                    isOpen={isVisualizeModalOpen}
                                    onRequestClose={closeVisualizeModal}
                                    contentLabel="Excel Visualization"
                                    style={{
                                        overlay: { backgroundColor: 'rgba(0,0,0,0.5)' },
                                        content: { 
                                            maxWidth: '90vw', 
                                            maxHeight: '90vh', 
                                            margin: 'auto',
                                            overflow: 'auto' 
                                        }
                                    }}
                                >
                                    {previousSummary && (
                                        <>
                                            <h2>Summary Table</h2>
                                            <button onClick={closeVisualizeModal} style={{ marginBottom: '20px' }}>
                                                Close
                                            </button>
                                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                                <thead>
                                                    <tr>
                                                        <th style={{ border: '1px solid #1c59b5', padding: '8px' }}>Variable</th>
                                                        <th style={{ border: '1px solid #1c59b5', padding: '8px' }}>Value</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {previousSummary.tableData.map(([key, value], rowIndex) => (
                                                        <tr key={rowIndex}>
                                                            <td style={{ border: '1px solid #1c59b5', padding: '8px' }}>{key}</td>
                                                            <td style={{ border: '1px solid #1c59b5', padding: '8px' }}>{value}</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </>
                                    )}
                                </Modal>

                                <button 
                                    onClick={() => handleEditName(summary)} 
                                    style={{ 
                                    fontSize: '16px',
                                    marginRight: '10px', 
                                    background: '#F5F5F5', 
                                    border: '1px solid #1c59b5',
                                    borderRadius: '3px',
                                    padding: '5px',
                                    cursor: 'pointer' 
                                    }} 
                                    title="Edit Name"
                                >
                                    &#9998;
                                </button>

                                <button 
                                    onClick={() => handleDownload(summary.editableName, summary.tableData)} 
                                    style={{ 
                                    fontSize: '16px',
                                    marginRight: '10px', 
                                    background: '#F5F5F5', 
                                    border: '1px solid #1c59b5',
                                    borderRadius: '3px',
                                    padding: '5px',
                                    cursor: 'pointer' 
                                    }} 
                                    title="Download"
                                >
                                    &#11015;
                                </button>

                                <button 
                                    onClick={() => handleDelete(summary)} 
                                    style={{ 
                                    fontSize: '16px',
                                    backgroundColor: '#F5F5F5',
                                    border: '1px solid #1c59b5',
                                    borderRadius: '3px',
                                    padding: '5px',
                                    cursor: 'pointer',
                                    }} 
                                    title="Delete"
                                >
                                    &#x1F5D1;
                                </button>
                    
                            </div>
                        </div>
                    ))}
                </div>
                
                <div className="validate-tender-title">
                    <h3>Validated Tender summaries</h3>
                </div>
                <div className="validate-tenders">
                    {generatedSummaries.filter(summary => summary.validation === true).map((summary, index) => (
                        <div key={index} className="generated-summary">
                            <div
                                style={{
                                    position: 'absolute',
                                    top: 0,
                                    left: 0,
                                    height: '100%',
                                    backgroundColor: 'green',
                                    width: `${(summary.tableData.filter(row => row[2] === 'Positive').length / summary.tableData.length) * 100}%`,
                                    zIndex: 0,
                                    opacity: 0.2,
                                }}
                                title={`Validation state at ${Math.round((summary.tableData.filter(row => row[2] === 'Positive').length / summary.tableData.length) * 100)}%`}
                            >

                            </div>
                            <div style={{ display: 'flex', alignItems: 'center' }}>
                                <button 
                                    onClick={() => handleValidate(summary)} 
                                    style={{ 
                                    fontSize: '16px',
                                    marginRight: '10px', 
                                    background: '#F5F5F5', 
                                    border: '1px solid #1c59b5',
                                    borderRadius: '3px',
                                    padding: '5px',
                                    cursor: 'pointer',
                                    zIndex: 1, 
                                    }} 
                                    title= "Validate summary"
                                >
                                &#x1F4BB;
                                </button>

                                <Modal
                                    isOpen={isValidateModalOpen}
                                    onRequestClose={closeValidateModal}
                                    contentLabel="Excel Visualization"
                                    style={{
                                        overlay: { backgroundColor: 'rgba(0,0,0,0.5)' },
                                        content: { 
                                            maxWidth: '90vw', 
                                            maxHeight: '90vh', 
                                            margin: 'auto',
                                            overflow: 'auto' 
                                        }
                                    }}
                                >
                                    {selectedSummary && (
                                        <>
                                            <h2>Summary Table Validation</h2>
                                            <button onClick={closeValidateModal} style={{ marginBottom: '20px', border: '1px solid #1c59b5' }}>
                                                Close
                                            </button>
                                            <button onClick={saveValidationChanges} style={{ marginBottom: '20px', marginLeft: '20px', border: '1px solid #1c59b5' }}>
                                                Save changes
                                            </button>
                                            <button onClick={correctWrongAnswers} style={{ marginBottom: '20px', marginLeft: '915px', border: '1px solid #1c59b5' }}>
                                                Correct wrong answers
                                            </button>

                                            {incorrectAnswers && (
                                                <>
                                                <h3 style={{
                                                    marginLeft: '630px',
                                                    bottom:'20px',
                                                    color:'black',
                                                    position: 'relative',
                                                     
                                                }}
                                                >
                                                    Choose variable to correct
                                                </h3>
                                                <button
                                                    onClick={() => setIsDropdownVisible(!isDropdownVisible)}
                                                    style={{
                                                        fontSize: '14px',
                                                        marginLeft: '650px',
                                                        bottom:'20px',
                                                        background: '#F5F5F5',
                                                        color:'black',
                                                        border: '1px solid #1c59b5',
                                                        borderRadius: '3px',
                                                        padding: '5px',
                                                        cursor: 'pointer',
                                                        position: 'relative',
                                                        maxWidth:'200px',
                                                        overflow: 'hidden', 
                                                    }}
                                                    title={selectedIncorrectAnswer}
                                                >
                                                    {selectedIncorrectAnswer}
                                                </button>
                                                <h3 style={{
                                                    marginLeft: '630px',
                                                    bottom:'20px',
                                                    color:'black',
                                                    position: 'relative',
                                                     
                                                }}
                                                >
                                                    Choose validation solution
                                                </h3>
                                                <button
                                                    onClick={() => setIsSolutionVisible(!isSolutionVisible)}
                                                    style={{
                                                        fontSize: '14px',
                                                        marginLeft: '650px',
                                                        bottom:'20px',
                                                        background: '#F5F5F5',
                                                        color:'black',
                                                        border: '1px solid #1c59b5',
                                                        borderRadius: '3px',
                                                        padding: '5px',
                                                        cursor: 'pointer',
                                                        position: 'relative',
                                                        maxWidth:'200px',
                                                        overflow: 'hidden', 
                                                    }}
                                                    title={selectedSolution}
                                                >
                                                    {selectedSolution}
                                                </button>
                                                </>
                                            )}

                                            {isDropdownVisible && (
                                                <ul ref={dropdownRef} style={{
                                                    position: 'absolute',
                                                    top: '180px',
                                                    left: '770px',
                                                    listStyleType: 'none',
                                                    padding: '0',
                                                    background: '#F5F5F5',
                                                    border: '1px solid #1c59b5',
                                                    borderRadius:'5px',
                                                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                                                    fontSize: '14px',
                                                    zIndex: '1000',
                                                }}>
                                                    {incorrectAnswers.map((name, index) => (
                                                        <li key={index}
                                                            onClick={() => {setIsDropdownVisible(false);
                                                                setSelectedIncorrectAnswer(name);}}
                                                            style={{
                                                                padding: '8px 16px',
                                                                cursor: 'pointer',
                                                                border: '1px solid #1c59b5',
                                                            }}
                                                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#e0e0e0'}
                                                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#F5F5F5'}
                                                        >
                                                            {name}
                                                        </li>
                                                    ))}
                                                </ul>
                                                
                                            )}
                                        
                                            {isSolutionVisible && (
                                                <ul ref={dropdownRef} style={{
                                                    position: 'absolute',
                                                    bottom: '340px',
                                                    left: '770px',
                                                    listStyleType: 'none',
                                                    padding: '0',
                                                    background: '#F5F5F5',
                                                    border: '1px solid #1c59b5',
                                                    borderRadius:'5px',
                                                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                                                    fontSize: '14px',
                                                    zIndex: '1000',
                                                }}>
                                                    {['Expert judgement solution', 'LLM supported solution'].map((name, index) => (
                                                        <li key={index}
                                                            onClick={() => {setIsSolutionVisible(false);
                                                                setSelectedSolution(name);}}
                                                            style={{
                                                                padding: '8px 16px',
                                                                cursor: 'pointer',
                                                                border: '1px solid #1c59b5',
                                                            }}
                                                            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#e0e0e0'}
                                                            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#F5F5F5'}
                                                        >
                                                            {name}
                                                        </li>
                                                    ))}
                                                </ul>
                                            )}

                                            {selectedSolution === 'Expert judgement solution' &&
                                            <form onSubmit={handleExpertSubmit} style={{ display: 'flex', marginTop: '10px' }}>
                                                <input
                                                    type="text"
                                                    value={inputExpert}
                                                    onChange={handleInputExpertChange}
                                                    className="chatbot-input"
                                                    placeholder="Type the correct answer to override the previous response"
                                                    style={{ flex: '1', padding: '5px', fontSize: '14px', marginLeft: '500px', marginBottom: '20px', color: 'black' }}
                                                />
                                                <button type="submit" style={{
                                                    fontSize: '14px',
                                                    background: '#1c59b5',
                                                    color: '#FFFFFF',
                                                    border: 'none',
                                                    borderRadius: '3px',
                                                    padding: '5px 10px',
                                                    cursor: 'pointer',
                                                    marginLeft: '20px',
                                                    marginBottom: '20px',
                                                }}>
                                                    Send
                                                </button>
                                            </form>}

                                            {selectedSolution === 'LLM supported solution' &&
                                                <form onSubmit={handleLlmSubmit} style={{ display: 'flex', flexDirection: 'column', marginTop: '10px' }}>
                                                    <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '20px' }}>
                                                        <input
                                                            type="text"
                                                            value={inputPrompt}
                                                            onChange={handleInputPromptChange}
                                                            className="chatbot-input"
                                                            placeholder="Type a sentence similar to how the variable could appear in the document."
                                                            style={{ flex: '1', padding: '5px', fontSize: '14px', marginRight: '10px', color: 'black' }}
                                                        />
                                                        <input
                                                            type="text"
                                                            value={inputLlm}
                                                            onChange={handleInputLlmChange}
                                                            className="chatbot-input"
                                                            placeholder="Formulate a precise question to help LLM return the expected response."
                                                            style={{ flex: '1', padding: '5px', fontSize: '14px', color: 'black' }}
                                                        />
                                                    </div>
                                                    <button type="submit" style={{
                                                        fontSize: '14px',
                                                        background: '#1c59b5',
                                                        color: '#FFFFFF',
                                                        border: 'none',
                                                        borderRadius: '3px',
                                                        padding: '5px 10px',
                                                        cursor: 'pointer',
                                                        alignSelf: 'center'
                                                    }}>
                                                        Submit
                                                    </button>
                                                </form>
                                            }
                                            

                                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                                <thead>
                                                    <tr>
                                                        <th style={{ border: '1px solid #1c59b5', padding: '8px' }}>Variable</th>
                                                        <th style={{ border: '1px solid #1c59b5', padding: '8px' }}>Value</th>
                                                        <th style={{ border: '1px solid #1c59b5', padding: '8px' }}>Validation</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {selectedSummary.tableData.map(([key, value, validationState], rowIndex) => (
                                                        <tr key={rowIndex}>
                                                            <td style={{ border: '1px solid #1c59b5', padding: '8px' }}>{key}</td>
                                                            <td style={{ border: '1px solid #1c59b5', padding: '8px' }}>{value}</td>
                                                            <td style={{ alignItems: 'center', justifyContent: 'space-between', border: '1px solid #1c59b5', padding: '8px' }}>
                                                                <button
                                                                    style={{ marginRight: '10px', cursor: 'pointer', border: '1px solid #1c59b5', backgroundColor: validationState === 'Positive' ? '#1c59b5' : 'transparent',
                                                                        color: validationState === 'Positive' ? 'white' : '#1c59b5'}}
                                                                    onClick={() => changeValidationState(rowIndex, 'Positive')}
                                                                >
                                                                    ✔️
                                                                </button>
                                                                <button
                                                                    style={{ cursor: 'pointer', border: '1px solid #1c59b5', backgroundColor: validationState === 'Negative' ? '#1c59b5' : 'transparent',
                                                                        color: validationState === 'Negative' ? 'white' : '#1c59b5' }}
                                                                    onClick={() => changeValidationState(rowIndex, 'Negative')}
                                                                >
                                                                    ❌
                                                                </button>
                                                            </td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </>
                                    )}
                                </Modal>
                            </div>
                            <p 
                            style={{ 
                                flexGrow: 1, 
                                whiteSpace: 'nowrap', 
                                overflow: 'hidden', 
                                textOverflow: 'ellipsis', 
                                margin: 0,
                                zIndex: 1,
                            }} 
                            title={summary.editableName}
                            >
                            {summary.editableName}
                            </p>
                        
                            <div style={{ display: 'flex', alignItems: 'center' }}>
                                <button 
                                    onClick={() => handleVisualize(summary)} 
                                    style={{ 
                                    fontSize: '16px',
                                    marginRight: '10px', 
                                    background: '#F5F5F5', 
                                    border: '1px solid #1c59b5',
                                    borderRadius: '3px',
                                    padding: '5px',
                                    cursor: 'pointer',
                                    zIndex: 1, 
                                    }} 
                                    title="Visualize"
                                >
                                    &#128065;
                                </button>

                                <Modal
                                    isOpen={isVisualizeModalOpen}
                                    onRequestClose={closeVisualizeModal}
                                    contentLabel="Excel Visualization"
                                    style={{
                                        overlay: { backgroundColor: 'rgba(0,0,0,0.5)' },
                                        content: { 
                                            maxWidth: '90vw', 
                                            maxHeight: '90vh', 
                                            margin: 'auto',
                                            overflow: 'auto' 
                                        }
                                    }}
                                >
                                    {previousSummary && (
                                        <>
                                            <h2>Summary Table</h2>
                                            <button onClick={closeVisualizeModal} style={{ marginBottom: '20px' }}>
                                                Close
                                            </button>
                                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                                <thead>
                                                    <tr>
                                                        <th style={{ border: '1px solid #1c59b5', padding: '8px' }}>Variable</th>
                                                        <th style={{ border: '1px solid #1c59b5', padding: '8px' }}>Value</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {previousSummary.tableData.map(([key, value], rowIndex) => (
                                                        <tr key={rowIndex}>
                                                            <td style={{ border: '1px solid #1c59b5', padding: '8px' }}>{key}</td>
                                                            <td style={{ border: '1px solid #1c59b5', padding: '8px' }}>{value}</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </>
                                    )}
                                </Modal>

                                <button 
                                    onClick={() => handleEditName(summary)} 
                                    style={{ 
                                    fontSize: '16px',
                                    marginRight: '10px', 
                                    background: '#F5F5F5', 
                                    border: '1px solid #1c59b5',
                                    borderRadius: '3px',
                                    padding: '5px',
                                    cursor: 'pointer',
                                    zIndex: 1, 
                                    }} 
                                    title="Edit Name"
                                >
                                    &#9998;
                                </button>

                                <button 
                                    onClick={() => handleDownload(summary.editableName, summary.tableData)} 
                                    style={{ 
                                    fontSize: '16px',
                                    marginRight: '10px', 
                                    background: '#F5F5F5', 
                                    border: '1px solid #1c59b5',
                                    borderRadius: '3px',
                                    padding: '5px',
                                    cursor: 'pointer',
                                    zIndex: 1, 
                                    }} 
                                    title="Download"
                                >
                                    &#11015;
                                </button>

                                <button 
                                    onClick={() => handleDelete(summary)} 
                                    style={{ 
                                    fontSize: '16px',
                                    backgroundColor: '#F5F5F5',
                                    border: '1px solid #1c59b5',
                                    borderRadius: '3px',
                                    padding: '5px',
                                    cursor: 'pointer',
                                    zIndex: 1,
                                    }} 
                                    title="Delete"
                                >
                                    &#x1F5D1;
                                </button>
                    
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="middle-side">
                <div className='upload-box'><FileUploader generatedSummaries={generatedSummaries} setGeneratedSummaries={setGeneratedSummaries} isLoading={isLoading} setIsLoading={setIsLoading} /></div>
                <Chatbot generatedSummaries={generatedSummaries} setGeneratedSummaries={setGeneratedSummaries}
                selectedConversation={selectedConversation} setSelectedConversation={setSelectedConversation}
                selectedTenderName={selectedTenderName} setSelectedTenderName={setSelectedTenderName}
                setIsExecuting={setIsExecuting} />
            </div>
            
            <div className="right-hand-side">
                <div className="conversation-title">
                    <h3>Tender chatbot conversations</h3>
                </div>
                <div className='conversations'>
                    {generatedSummaries.map((summary, index) => (
                        <React.Fragment key={index}>
                            <div className="conversation-folder">
                                <p
                                    style={{
                                        flexGrow: 1,
                                        whiteSpace: 'nowrap',
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                        margin: 0,
                                    }}
                                    title={summary.editableName}
                                >
                                    {summary.editableName}
                                </p>
                                <div style={{ display: 'flex', gap: '10px' }}>
                                        <button 
                                            onClick={() => addNewConversation(summary)}
                                            style={{ 
                                            fontSize: '16px',
                                            marginRight: '10px', 
                                            background: '#F5F5F5', 
                                            border: '1px solid #1c59b5',
                                            borderRadius: '3px',
                                            padding: '5px',
                                            cursor: 'pointer' 
                                            }} 
                                            title="Add new conversation"
                                        >
                                            &#43;
                                        </button>
                                        <button
                                            onClick={() => toggleConversationVisibility(index)}
                                            style={{
                                                fontSize: '16px',
                                                marginRight: '10px',
                                                background: '#F5F5F5',
                                                border: '1px solid #1c59b5',
                                                borderRadius: '3px',
                                                padding: '5px',
                                                cursor: 'pointer',
                                            }}
                                            title={visibleConversations[index] ? "Hide conversations" : "Show conversations"}
                                        >
                                            {visibleConversations[index] ? '\u23EB' : '\u23EC'}
                                        </button>
                                    </div>
                                
                            </div>
                            {visibleConversations[index] && summary.conversations.map((conversation, convIndex) => (
                                <div
                                key={convIndex}
                                className="conversation"
                                onClick={() => handleSelectConversationAndTenderName(summary, conversation)}
                                style={{ cursor: 'pointer' }}
                                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#F5F5F5'}
                                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#FFFFFF'}
                            >
                                    <p>{conversation.nameConversation}</p>

                                    <div style={{ display: 'flex', gap: '10px' }}>
                                        <button 
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleEditConversationName(summary, conversation);
                                            }}
                                            style={{ 
                                            fontSize: '16px',
                                            marginRight: '10px', 
                                            background: '#F5F5F5', 
                                            border: '1px solid #1c59b5',
                                            borderRadius: '3px',
                                            padding: '5px',
                                            cursor: 'pointer' 
                                            }} 
                                            title="Edit conversation name"
                                        >
                                            &#9998;
                                        </button>
                                        <button 
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleDeleteConversation(summary, conversation);
                                            }}
                                            style={{ 
                                            fontSize: '16px',
                                            backgroundColor: '#F5F5F5',
                                            border: '1px solid #1c59b5',
                                            borderRadius: '3px',
                                            padding: '5px',
                                            cursor: 'pointer',
                                            }} 
                                            title="Delete conversation"
                                        >
                                            &#x1F5D1;
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </React.Fragment>
                    ))}
                </div>

            </div>
        </div>
    );
};

export default Body;
