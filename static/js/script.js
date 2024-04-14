document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const pdfPreview = document.getElementById('pdfPreview');
    const prevPageButton = document.getElementById('prev-page');
    const nextPageButton = document.getElementById('next-page');
    const pageNumDisplay = document.getElementById('page-num');
    const pageCountDisplay = document.getElementById('page-count');
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    let pdfDoc = null;
    let pageNum = 1;

    prevPageButton.addEventListener('click', onPrevPage);
    nextPageButton.addEventListener('click', onNextPage);
    prevPageButton.disabled = true;
    nextPageButton.disabled = true;

    function onPrevPage() {
        if (pageNum <= 1) {
            return;
        }
        pageNum--;
        queueRenderPage(pageNum);
    }

    function onNextPage() {
        if (pageNum >= pdfDoc.numPages) {
            return;
        }
        pageNum++;
        queueRenderPage(pageNum);
    }

    function renderPage(num) {
        pdfDoc.getPage(num).then((page) => {
            const viewport = page.getViewport({ scale: 1 });
            canvas.height = viewport.height;
            canvas.width = viewport.width;
            pdfPreview.appendChild(canvas);

            const renderContext = {
                canvasContext: ctx,
                viewport: viewport
            };

            page.render(renderContext).promise.then(() => {
                prevPageButton.disabled = pageNum <= 1;
                nextPageButton.disabled = pageNum >= pdfDoc.numPages;
            });

            pageNumDisplay.textContent = num;
        });
    }

    function queueRenderPage(num) {
        if (pdfDoc !== null) {
            renderPage(num);
        }
    }

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        fetch('/upload', {  // Make sure this matches your server-side URL
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            console.log('File uploaded successfully:', data);
            // You can also update the UI to show the upload status
        })
        .catch(error => {
            console.error('Error uploading file:', error);
        });
    }
    
    function handleFiles(file) {
        if (file.type !== 'application/pdf') {
            alert('Please upload a PDF file.');
            return;
        }

        pdfjsLib.getDocument({url: URL.createObjectURL(file)}).promise.then((pdfDoc_) => {
            pdfDoc = pdfDoc_;
            pageNum = 1; // Reset to first page for new document
            pageCountDisplay.textContent = pdfDoc.numPages;
            prevPageButton.disabled = pageNum <= 1;
            nextPageButton.disabled = pageNum >= pdfDoc.numPages;

            renderPage(pageNum);
            uploadFile(file);
        });
    }

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFiles(file);
        }
    });

    const dropZone = document.getElementById('pdfInput');
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length) {
            handleFiles(files[0]);
        }
    });
});
