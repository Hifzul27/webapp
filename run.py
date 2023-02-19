from flask import Flask, request, jsonify, render_template
from azure.storage.blob import BlobServiceClient
from datetime import datetime
from io import BytesIO
from flask import make_response

app = Flask(__name__)

# Azure Storage Account Details
account_name = 'demoaccount2706'
account_key = 'GGfsvX8wQmc7p7Dv0EETUrpJOn13dY/w45t3nL5m98SzPgS1F5gdwCCLtDXEyVdcDK0lPDu6EzSE+AStp9x20g=='
container_name = 'image'

# Create the Blob Service
blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net/", credential=account_key)

from datetime import datetime

@app.route('/')
def index():
    return render_template('index.html')


from PIL import Image, ImageFilter

from PIL import Image, ImageFilter

@app.route('/upload', methods=['POST'])
def upload_image():
    # Check if the POST request contains a file
    if 'file' not in request.files:
        return jsonify({'error': 'No file in the request'}), 400

    file = request.files['file']
    # Check if the file is an image
    if file.content_type.split('/')[0] != 'image':
        return jsonify({'error': 'Invalid file type'}), 400


    # Set the new filename with the date and time
    new_filename = 'filtered_' + file.filename

    # Open the uploaded image
    img = Image.open(file.stream)

    # Convert the image to grayscale
    bw_img = img.convert('L')

    # Save the black and white image to a BytesIO object
    output = BytesIO()
    bw_img.save(output, format='JPEG')
    bw_img_bytes = output.getvalue()

    # Upload the black and white image to Azure Blob Storage with the new filename
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=new_filename)
    blob_client.upload_blob(bw_img_bytes, overwrite=True)

    return jsonify({'message': 'File uploaded successfully with new name ' + new_filename}), 200



@app.route('/list_files', methods=['GET'])
def list_files():
    # Create a list to store the URLs
    urls = []

    # Get a reference to the container
    container_client = blob_service_client.get_container_client(container_name)

    # List all the blobs in the container
    blob_list = container_client.list_blobs()

    # Append the URLs to the list
    for blob in blob_list:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob.name)
        urls.append(blob_client.url)

    # Create a response with the list of URLs
    response = make_response(jsonify({'urls': urls}), 200)

    # Set the Content-Type header for each URL
    for url in urls:
        if url.endswith('.jpg') or url.endswith('.jpeg'):
            response.headers.set('Content-Type', 'image/jpeg')
        elif url.endswith('.png'):
            response.headers.set('Content-Type', 'image/png')
        elif url.endswith('.gif'):
            response.headers.set('Content-Type', 'image/gif')

    return response

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
