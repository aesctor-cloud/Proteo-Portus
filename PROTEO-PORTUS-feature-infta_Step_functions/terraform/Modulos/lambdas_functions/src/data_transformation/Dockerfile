FROM public.ecr.aws/lambda/python:3.11

COPY . ${LAMBDA_TASK_ROOT}

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


CMD ["main.handler"]