# Extract Info

This project is created with the idea of being able to extract information from really old, scanned documents.

The primary issue that is noted is that many of these documents can't be directly parsed by LLM's and explicit OCR is needed.

OCR is, in fact, the most pivotal requirement here and a lot of the output quality depends solely on how well OCR is performing on the PDF.

## Installation

```bash
pip install -r requirements.txt
apt install ocrmypdf
```

To run:

```
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload
```

## Brief Process

Step 1. OCR is used at first to be able to create some readable text. This is a very important step, as most scanned documents might not contain text in the normal form that is parseable by simple PDF Parsers.

Step 2. Extract the text from a PDF parser, like PDFPlumber.

Step 3. Pass the text to a LLM (OpenAI GPT 4) to receive a JSON output with the troubleshooting information.

## Caveats

### DE_GAN

Since OCR is the most important part for being able to extract text, we use DE_GAN to enhance the images.
We deblur the images, where each image is captured at a page level of the PDF.
The images are then stitched back into a PDF before passing to the OCR function.

_Note_: This however can be a time consuming method for running on a CPU only backend, hence is by default turned off. You can see the code for this in `server/pdf_utils.py`.

### Google Maxim

Maxim is another model that can be used for image enhancement but again, this is quite time consuming for larger PDFs, specifically on a CPU.

An alternative is to use the hosted model on [`Replicate`](https://replicate.com/google-research/maxim).
My experiments with it have led me to believe that `Image Deblurring (RealBlur_R)` is the best model for this specific task.

Here is a sample :

Code snippet of how `Maxim on Replicate` can be used in place of `DE_GAN`:

```python
import os
import logging
import requests
import replicate

def download_image(url, output_path):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(output_path, 'wb') as out_file:
        out_file.write(response.content)
    logging.info(f"Downloaded image from {url} to {output_path}")

def process_images(image_dir, model_name, client):
    for image_name in os.listdir(image_dir):
        image_path = os.path.join(image_dir, image_name)
        with open(image_path, "rb") as image_file:
            input_data = {
                "image": image_file,
                "model": model_name
            }
            output_url = client.run(
                "google-research/maxim:494ca4d578293b4b93945115601b6a38190519da18467556ca223d219c3af9f9",
                input=input_data,
            )
            logging.info(f"Processed image {image_name}, output at {output_url}")
            download_image(output_url, f"output_{image_name}")

def main():
    logging.basicConfig(level=logging.INFO)
    image_dir = "./images"
    model_name = "Image Deblurring (RealBlur_R)"
    api_token = os.environ.get("REPLICATE_API_TOKEN", None)
    client = replicate.Client(api_token=api_token)
    process_images(image_dir, model_name, client)

```

### LDMSuperResolution

`LDMSuperResolution` is a diffusers model that does super resolution on images. It can be accessed quite easily through `LDMSuperResolutionPipeline` from the `diffusers` package.

However, this doesn't work very well in our case cause the AI model is not trained for text documents and hence the output is garbled.

## Evaluations

### OCR

Following are methods evaluated for OCR:

#### Amazon Textract

Not as useful here and output quality is not as good.

#### Google Cloud Vision

Performs exceptionally well but hasn't been integrated here due to cost. If the budget permits, this should be the go to method.

#### Other PDF Libraries

1. OCRMyPDF

This works best as it actually does OCR and this is what we use to save out on costs.

2. PDF Plumber

Unable to parse the original PDF but works well with the output from OCRMyPDF.

3. PyMuPDF

Unable to parse the original PDF. Nor does it work well with the output from OCRMyPDF.

### Language Models

Now that we have the text available to us, we need to be able to identify troubleshooting information from it.
To be able to do that we use `Langchain`, which gives us a streamlined way to maintain and talk to various LLMs.

Currently we support only `OpenAI`, and it's various models, but it is equally simple to add other models in in `server/models.py`.

#### OpenAI GPT 3.5

Works okay, but not able to identify the correct troubleshooting information.

#### OpenAI GPT 4 - Turbo

Works best, among the OpenAI models.

#### Gemini Pro 1.5

Works better than all models. Comes integrated with Google Cloud Vision so the output is far better than other models.
In fact, if we are using Gemini then we don't even need to do OCR or text extraction from the PDF. Directly passing the PDF works.

Here is some sample code of how `Gemini Pro 1.5` can be used, with a workaround as the API is not available in all regions!

```python
import vertexai
from server.constants import PROMPT_PREFIX

from vertexai.generative_models import GenerativeModel, Part

vertexai.init(project=project_id, location="us-central1")  # setting the location to one where API access is allowed!

model = GenerativeModel(model_name="gemini-1.5-pro-latest")

prompt = PROMPT_PREFIX

pdf_file_uri = "gs://..."  # path to your uploaded PDF
pdf_file = Part.from_uri(pdf_file_uri, mime_type="application/pdf")
contents = [pdf_file, prompt]

response = model.generate_content(contents)
print(response.text)
```

_Note_: The caveat with Gemini is that it doesn't return in `JSON` most of the time. This needs to be explicitly taken care of and one can use `Gemini` with `Langchain` to overcome this.
