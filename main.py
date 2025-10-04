from fasthtml.common import *
import boto3
import os

ACCESS_KEY_ID= os.environ.get('AWS_ACCESS_KEY_ID')
SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = os.environ.get('AWS_S3_BUCKET_NAME')
ENDPOINT_URL = os.environ.get('AWS_ENDPOINT_URL')


s3_client = boto3.client('s3', endpoint_url=ENDPOINT_URL, aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY)


js = '''

document.body.addEventListener('htmx:afterRequest', function(evt) {
    // Your JavaScript code to execute after any HTMX request
    console.log('HTMX request finished:', evt.detail.xhr.status);
    // AWS sends back a 204 response code on successful upload
    if (evt.detail.xhr.status === 204){
      console.log("FILE UPLOADED")
      const img_holder = document.getElementById('result-one');
      img_holder.click();
      const fileInputForm = document.getElementById('upload_form');
      fileInputForm.reset()
    }
});

// Assuming you have an input element with type="file" and id="fileInput"
const fileInput = document.getElementById('fileInput');
fileInput.addEventListener('change', (event) => {
  const fileName = event.target.files[0].name
  const fileNameInput = document.getElementById('filename');
  fileNameInput.setAttribute("value", fileName);
  const fileNameAfter = document.getElementById('filename_after');
  fileNameAfter.setAttribute("value", fileName);
  fileNameInput.click();
});
'''

app, rt = fast_app(static_path="public", hdrs=(Meta(name="htmx-config", content='{"selfRequestsOnly": false}'), Link(href="static/index.js", type="text/javascript")))

@rt('/')
def get():
    return Titled(
        "File Upload Demo",
        Article(
            Div("Click to upload image", role="button", hx_get="/upload", hx_swap="outerHTML")
        )
    )

@rt('/upload')
def get():
    return Div(
                # Actual Upload form.  Users interact with this form and it submits to S3
            Form(hx_post=f'{ENDPOINT_URL}/{BUCKET_NAME}', id="upload_form")(
                    # Signed inputs end up here
                Div(id="signed_inputs"),
                    # Normal File input
                    Input(type="file", name="file", id="fileInput"),
                    Button("Upload", type="submit", cls='secondary'),
                ),
                # A hidden input that holds the file name.  This is submitted to get the signature details on change of the file input
                # This behaviour is handled by JS lines 33-41 of this file.
                Input(
                    type="hidden",
                    name="filename",
                    id="filename",
                    hx_post="uploadName",
                    hx_trigger="click",
                    hx_target="#signed_inputs",
                ),

            Form(
                Input(
                    type="text",
                    name="filename",
                    id="filename_after",
                )
               ,
                id="result-one", hx_get="/signedurl", hx_trigger="click", hx_target="#upload_form",
                style="display: none;",
            ),
            Surreal(js)
        )

@rt('/signedurl')
def get(request:Request):
    object_name = request.query_params['filename']
    # Could also persist information about the image here.
    # Getting a callback after successful upload is an opportunity to do many things.
    signedURL = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': object_name},
        ExpiresIn=3600
    )
    return Div(
        Img(src=f"{signedURL}"),
            Div(
                "Upload Another Image",
                role="button",
                hx_get="/upload",
                hx_target="#img_holder"
            ),
    id="img_holder"
    )

@rt('/uploadName')
async def post(request: Request):
    form = await request.form()
    filename = form.get("filename")
    print(filename)
    presigned_post = s3_client.generate_presigned_post(
        Bucket=BUCKET_NAME,
        Key=f'{filename}',
        ExpiresIn=3600  # URL valid for 1 hour
    )
    return Div(
        Input(type="hidden", name="key", value=presigned_post['fields']["key"]),
        Input(type="hidden", name="AWSAccessKeyId", value=presigned_post['fields']["AWSAccessKeyId"]),
        Input(type="hidden", name="policy", value=presigned_post['fields']["policy"]),
        Input(type="hidden", name="signature", value=presigned_post['fields']["signature"]),
    )


serve()