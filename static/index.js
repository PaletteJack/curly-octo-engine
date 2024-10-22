function capitalize(string) {
    splitString = string.split("_")
    capitalizedList = splitString.map(item => {
          return item[0].toUpperCase() + item.slice(1)
      });
    return capitalizedList.join(" ")
}

async function runQuery() {
    const query = document.getElementById('query').value;
    const resultsDiv = document.getElementById('results');
    
    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        resultsDiv.innerHTML = '<h2>Results:</h2>';

        if (!Array.isArray(data)) {
            throw new Error('Unexpected response format');
        }

        if (data.length === 0) {
            resultsDiv.innerHTML += '<p>No results found.</p>';
            return;
        }

        const table = document.createElement('table');
        
        // Create header row
        const headerRow = table.insertRow();
        for (const key in data[0]) {
            const th = document.createElement('th');
            th.textContent = capitalize(key);
            headerRow.appendChild(th);
        }

        // Create data rows
        data.forEach(item => {
            const row = table.insertRow();
            for (const key in item) {
                const cell = row.insertCell();
                cell.textContent = item[key];
            }
        });

        resultsDiv.appendChild(table);

    } catch (error) {
        console.error('Error:', error);
        resultsDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    }
}

async function exportQuery() {
    const query = document.getElementById('query').value;

    try {
        const response = await fetch('/export', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'query_export.csv';
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
            if (filenameMatch) {
                filename = filenameMatch[1];
            }
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

    } catch (error) {
        console.error('Error:', error);
        alert('Failed to export CSV: ' + error.message);
    }
}

function openDialog() {
    const modal = document.querySelector("dialog")
    modal.showModal()
}

function closeDialog() {
    const modal = document.querySelector("dialog")
    modal.close()
}