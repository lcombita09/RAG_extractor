import './styles/components.css';
import React, { useState, useEffect, useRef } from 'react';

const Chatbot = ({ generatedSummaries, setGeneratedSummaries,
    selectedConversation, setSelectedConversation,
    selectedTenderName, setSelectedTenderName,
    setIsExecuting }) => {
    const [isDropdownVisible, setIsDropdownVisible] = useState(false);
    const [inputText, setInputText] = useState('');

    // Ref for dropdown menu
    const dropdownRef = useRef(null);
    // Ref to always see the bottom of conversation when new message is generated
    const chatContainerRef = useRef(null);

    const editTableNames = generatedSummaries.map(summary => summary.editableName);

    // Handler when a tender name is selected
    const handleTenderSelect = (name) => {
        setIsDropdownVisible(false);
    
        // Find the selected summary by name
        const selSummary = generatedSummaries.find(summary => summary.editableName === name);
    
        // If the selected name is different from the current selected tender name
        if (name !== selectedTenderName) {
            // Check if there's an existing conversation with the name "New conversation"
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
        }
    
        setSelectedTenderName(name);
    };
    

    // Handle input text change
    const handleInputChange = (e) => {
        setInputText(e.target.value);
    };

    // Handle form submission
    const handleSubmit = async (e) => {
        e.preventDefault();

        if (inputText.trim()) {
            // Clear the input field after submission
            setInputText('');

            // Set executing to true when the process starts
            setIsExecuting(true);

            setGeneratedSummaries(prevSummaries => 
                prevSummaries.map(summary => {
                    if (summary.editableName === selectedTenderName) {
                        return {
                            ...summary,
                            conversations: summary.conversations.map(conversation => {
                                if (conversation.id === selectedConversation.id) {
                                    const updatedConversation = {
                                        ...conversation,
                                        fullConversation: [...conversation.fullConversation, inputText],
                                        nameConversation: conversation.nameConversation === "New conversation" ? inputText : conversation.nameConversation
                                    };

                                    // Correct placement of setSelectedConversation
                                    setSelectedConversation(updatedConversation);

                                    return updatedConversation;
                                }
                                return conversation;
                            })
                        };
                    }
                    return summary;
                })
            );

            // Find the summary object where editableName matches selectedTenderName
            const matchingSummary = generatedSummaries.find(summary => summary.editableName === selectedTenderName);


            try {
                const response = await fetch('http://127.0.0.1:8000/chatbot', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        vectorstore_name: matchingSummary.uploadFileName,
                        input_text: inputText,
                        chat_history: selectedConversation.fullConversation,
                    })
                });
            
                const reader = response.body.getReader();
                const decoder = new TextDecoder('utf-8');
                let done = false;
            
                // Create a new message div as soon as the response starts streaming
                setGeneratedSummaries(prevSummaries => 
                    prevSummaries.map(summary => {
                        if (summary.editableName === selectedTenderName) {
                            return {
                                ...summary,
                                conversations: summary.conversations.map(conversation => {
                                    if (conversation.id === selectedConversation.id) {
                                        const updatedConversation = {
                                            ...conversation,
                                            fullConversation: [...conversation.fullConversation, ""]
                                        };
            
                                        setSelectedConversation(updatedConversation);
            
                                        return updatedConversation;
                                    }
                                    return conversation;
                                })
                            };
                        }
                        return summary;
                    })
                );
            
                let responseText = '';
            
                // While streaming is not done, keep processing chunks
                while (!done) {
                    const { value, done: readerDone } = await reader.read();
                    done = readerDone;
            
                    if (value) {
                        // Decode the chunk of response data
                        const chunk = decoder.decode(value, { stream: !done });
                        responseText += chunk; // Append the chunk to the growing response text
            
                        // Update the specific message div in the conversation with the streamed chunk
                        setGeneratedSummaries(prevSummaries => 
                            prevSummaries.map(summary => {
                                if (summary.editableName === selectedTenderName) {
                                    return {
                                        ...summary,
                                        conversations: summary.conversations.map(conversation => {
                                            if (conversation.id === selectedConversation.id) {
                                                const updatedMessages = conversation.fullConversation.map((msg, index) => {
                                                    // Find the last message (empty string we created initially)
                                                    if (index === conversation.fullConversation.length - 1) {
                                                        // Append the chunk to the last (newly created) message
                                                        return msg + chunk;
                                                    }
                                                    return msg;
                                                });
            
                                                const updatedConversation = {
                                                    ...conversation,
                                                    fullConversation: updatedMessages
                                                };
            
                                                setSelectedConversation(updatedConversation);
            
                                                return updatedConversation;
                                            }
                                            return conversation;
                                        })
                                    };
                                }
                                return summary;
                            })
                        );
                    }
                }
            } catch (error) {
                console.error('Error fetching the stream:', error);
            } finally {
                // Set loading to false when operation is done or in case of error
                setIsExecuting(false);
            }

        }
    };

    

    // Close the dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsDropdownVisible(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    // Scroll to the bottom when new messages are added
    useEffect(() => {
        if (chatContainerRef.current) {
        chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [selectedConversation]);


    return (
        <div className="chatbot">
            <div className="chatbot-content" ref={chatContainerRef}>
                {selectedConversation?.fullConversation.length > 0 ? (
                    selectedConversation.fullConversation.map((message, index) => (
                        <div
                            key={index}
                            className={index % 2 === 0 ? 'human-message' : 'bot-message'}
                        >
                            {message}
                        </div>
                    ))
                ) : (
                    <div>Choose a tender and type below to start a new conversation.</div>
                )}
            </div>

            <div className="chatbot-banner">
                <button
                    onClick={() => setIsDropdownVisible(!isDropdownVisible)}
                    style={{
                        fontSize: '14px',
                        marginRight: '10px',
                        bottom:'-4.2px',
                        background: '#F5F5F5',
                        color:'#1c59b5',
                        border: '1px solid #1c59b5',
                        borderRadius: '3px',
                        padding: '5px',
                        cursor: 'pointer',
                        position: 'relative',
                        maxWidth:'90px',
                        maxHeight: '45px',
                        overflow: 'hidden', 
                    }}
                    title={selectedTenderName}
                >
                    {selectedTenderName}
                </button>

                {isDropdownVisible && (
                    <ul ref={dropdownRef} style={{
                        position: 'absolute',
                        bottom: '70px',
                        left: '390px',
                        listStyleType: 'none',
                        padding: '0',
                        background: '#F5F5F5',
                        border: '1px solid #1c59b5',
                        borderRadius:'5px',
                        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                        fontSize: '14px',
                        zIndex: '1000',
                    }}>
                        {editTableNames.map((name, index) => (
                            <li key={index}
                                onClick={() => handleTenderSelect(name)}
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

                <form onSubmit={handleSubmit} style={{ display: 'flex', marginTop: '10px' }}>
                    <input
                        type="text"
                        value={inputText}
                        onChange={handleInputChange}
                        className="chatbot-input"
                        placeholder="Select a tender file or open up an existing conversation to start a chat"
                        style={{ flex: '1', padding: '5px', fontSize: '14px' }}
                    />
                    <button type="submit" style={{
                        fontSize: '14px',
                        background: '#1c59b5',
                        color: '#FFFFFF',
                        border: 'none',
                        borderRadius: '3px',
                        padding: '5px 10px',
                        cursor: 'pointer',
                        marginLeft: '10px'
                    }}>
                        Send
                    </button>
                </form>
            </div>
        </div>
    );
};

export default Chatbot;
