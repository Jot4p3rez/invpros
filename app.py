from flask import Flask, render_template, request, jsonify, send_file
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['REPORTS_FOLDER'] = 'reports'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)


@app.route('/')
def inventory_crossing():
    return render_template('inventory_crossing.html')


@app.route('/api/process-inventory', methods=['POST'])
def process_inventory():
    try:
        wms_file = request.files['wmsFile']
        upc_file = request.files['upcFile']
        erp_file = request.files['erpFile']

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        wms_path = os.path.join(
            app.config['UPLOAD_FOLDER'], f"wms_{timestamp}_{secure_filename(wms_file.filename)}")
        upc_path = os.path.join(
            app.config['UPLOAD_FOLDER'], f"upc_{timestamp}_{secure_filename(upc_file.filename)}")
        erp_path = os.path.join(
            app.config['UPLOAD_FOLDER'], f"erp_{timestamp}_{secure_filename(erp_file.filename)}")

        wms_file.save(wms_path)
        upc_file.save(upc_path)
        erp_file.save(erp_path)

        config = {
            "ruta_archivo_wms": wms_path,
            "nombre_hoja_wms": request.form.get('wmsSheet', 'Sheet1'),
            "col_item_wms": request.form.get('wmsItemCol', 'Item'),
            "col_on_hand_wms": request.form.get('wmsStockCol', 'On Hand'),
            "ruta_archivo_upc_sku": upc_path,
            "col_sku_en_upc_para_wms": request.form.get('upcSkuCol', 'SKU'),
            "col_busr8_upc_sku": request.form.get('upcBusr8Col', 'BUSR8'),
            "ruta_archivo_erp": erp_path,
            "nombre_hoja_erp": request.form.get('erpSheet', 'Sheet1'),
            "col_clave_erp_para_busr8": request.form.get('erpSkuCol', 'Sku'),
            "col_stock_erp": request.form.get('erpStockCol', 'Stock On Hand'),
            "ruta_carpeta_salida": app.config['REPORTS_FOLDER'],
            "nombre_base_reporte": f"inventory_report_{timestamp}",
            "formato_fecha_salida": "%Y%m%d%H%M%S"
        }

        from invpros import process_inventories
        result = process_inventories(config)

        report_files = [f for f in os.listdir(app.config['REPORTS_FOLDER'])
                        if f.startswith(f"inventory_report_{timestamp}")]

        if report_files:
            report_filename = report_files[0]
        else:
            report_filename = None

        return jsonify({
            "success": True,
            "log": result,
            "report_filename": report_filename
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/download-report/<filename>')
def download_report(filename):
    return send_file(
        os.path.join(app.config['REPORTS_FOLDER'], filename),
        as_attachment=True,
        download_name=f"inventory_report_{datetime.now().strftime('%Y%m%d%H%M')}.xlsx"
    )


if __name__ == '__main__':
    app.run(debug=True)
