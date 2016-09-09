from python:3-onbuild

entrypoint ["python", "-m", "icsfilter", "serve"]

expose 80
