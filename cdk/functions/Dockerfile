FROM public.ecr.aws/lambda/python:3.11

# Install system dependencies for image processing
RUN dnf update -y && \
    dnf install -y gcc gcc-c++ libjpeg-turbo-devel libpng-devel freetype-devel && \
    dnf clean all

# Install Python dependencies
RUN pip install --no-cache-dir Pillow==10.0.0 boto3

# Copy function code
COPY image_resizer_quality.py ${LAMBDA_TASK_ROOT}/lambda_function.py

# Set the CMD to your handler
CMD [ "lambda_function.handler" ]