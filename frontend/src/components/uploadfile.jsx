import React, { useState } from 'react';
import './styles/components.css';

function FileUploader({ generatedSummaries, setGeneratedSummaries, isLoading, setIsLoading }) {
    const [fileName, setFileName] = useState(null);
    const [file, setFile] = useState(null);

    // Handle file selection
    const handleFileChange = (event) => {
        const selectedFile = event.target.files[0];

        // Check if the selected file is a PDF
        if (selectedFile && selectedFile.type !== 'application/pdf') {
            alert('Only PDF files are allowed.');
            document.getElementById('file-upload').value = null; // Reset file input
            return;
        }

        const baseName = selectedFile.name.replace(/\.pdf$/, '');

        // Check if the file was already uploaded
        const existingSummary = generatedSummaries.find(summary => summary.uploadFileName === baseName);

        if (existingSummary) {
            alert(`File was already uploaded. Its current name is "${existingSummary.editableName}".`);
            document.getElementById('file-upload').value = null; // Reset file input
            return;
        }

        if (selectedFile) {
            setFileName(baseName); // Set the file name for display
            setFile(selectedFile); // Store the selected file
        }
    };

    // Handle file upload and summary generation
    const handleUpload = async () => {
        if (!file) {
            alert("You need to load a tender first!");
            return;
        }

        setIsLoading(true);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://127.0.0.1:8000/get_resume', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('An error occurred');
            }

            const jsonResponse = await response.json();
            
            const transformedData = Object.entries(jsonResponse);

            // Add validation state to each array
            const finalTransformedData = transformedData.map(([key, value]) => [key, value, 'None']);

            // Store summary data as an object containing data and functions
            const newSummary = {
                uploadFileName: fileName,
                editableName: fileName,
                tableData: finalTransformedData,
                conversations: [],
                validation: false,
                ragResult: jsonResponse.rag_result, // Guardamos rag_result
            };

            // Add new summary data to the list
            setGeneratedSummaries((prevSummaries) => [...prevSummaries, newSummary]);
        } catch (error) {
            console.error('Error uploading the file:', error);
        } finally {
            setFileName(null);
            setFile(null);
            setIsLoading(false);
            document.getElementById('file-upload').value = null;
        }
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
            <label htmlFor="file-upload" className="custom-file-upload">
                Choose tender file
            </label>
            <input 
                id="file-upload" 
                type="file" 
                accept=".pdf"
                onChange={handleFileChange} 
                style={{ display: 'none' }} 
                disabled={isLoading}
            />
            {fileName && <p>Selected File: {fileName}</p>}
            
            <button 
                onClick={handleUpload} 
                style={{ fontFamily: 'Futura Now Text, Open Sans, sans-serif', color: '#1c59b5' }} 
                disabled={isLoading}
            >
                {isLoading ? 'Generating...' : 'Generate tender summary'}
            </button>
        </div>
    );
}

export default FileUploader;
