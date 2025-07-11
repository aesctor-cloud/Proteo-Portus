FROM public.ecr.aws/lambda/python:3.11

COPY . ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt

CMD ["main.handler"]