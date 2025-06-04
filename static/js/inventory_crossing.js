document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('inventoryForm');
    const processBtn = document.getElementById('processBtn');
    const processText = document.getElementById('processText');
    const processSpinner = document.getElementById('processSpinner');
    const resultsContainer = document.getElementById('resultsContainer');
    const processLog = document.getElementById('processLog');
    const wmsFileInput = document.getElementById('wmsFile');
    const upcFileInput = document.getElementById('upcFile');
    const erpFileInput = document.getElementById('erpFile');

    processBtn.disabled = true;

    function checkFiles() {
        const wmsFile = wmsFileInput.files.length > 0;
        const upcFile = upcFileInput.files.length > 0;
        const erpFile = erpFileInput.files.length > 0;

        document.querySelectorAll('.file-loaded').forEach(indicator => indicator.classList.add('d-none'));

        if (wmsFile) {
            wmsFileInput.parentNode.querySelector('.file-loaded').classList.remove('d-none');
        }
        if (upcFile) {
            upcFileInput.parentNode.querySelector('.file-loaded').classList.remove('d-none');
        }
        if (erpFile) {
            erpFileInput.parentNode.querySelector('.file-loaded').classList.remove('d-none');
        }
        processBtn.disabled = !(wmsFile && upcFile && erpFile);
    }

    wmsFileInput.addEventListener('change', checkFiles);
    upcFileInput.addEventListener('change', checkFiles);
    erpFileInput.addEventListener('change', checkFiles);

    form.addEventListener('submit', function (e) {
        e.preventDefault();

        processBtn.disabled = true;
        processText.textContent = "Procesando...";
        processSpinner.classList.remove('d-none');
        resultsContainer.classList.add('d-none');

        const formData = new FormData();

        Swal.fire({
            title: 'Procesando inventarios',
            html: 'Por favor espera mientras se genera el reporte...',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });
        fetch('/api/process-inventory', {
            method: 'POST',
            body: formData
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    processLog.innerHTML = data.log.replace(/\n/g, '<br>');
                    resultsContainer.classList.remove('d-none');
                    Swal.fire({
                        title: '¡Proceso completado!',
                        html: 'El reporte se ha generado correctamente.<br><br>' +
                            data.log.replace(/\n/g, '<br>'),
                        icon: 'success',
                        confirmButtonText: 'Descargar Reporte',
                        showCancelButton: true,
                        cancelButtonText: 'Cerrar',
                        allowOutsideClick: false
                    }).then((result) => {
                        if (result.isConfirmed) {
                            window.location.href = `/api/download-report/${data.report_filename}`;
                        }
                    });
                } else {
                    Swal.fire({
                        title: 'Error en el proceso',
                        text: data.error,
                        icon: 'error'
                    });
                }
            })
            .catch(error => {
                Swal.fire({
                    title: 'Error de conexión',
                    text: error.message,
                    icon: 'error'
                });
            })
            .finally(() => {
                processText.textContent = "Procesar Inventarios";
                processSpinner.classList.add('d-none');
                checkFiles();
            });
    });
});