FROM ubuntu:20.04
RUN pip3 install -r requirements.txt
RUN chmod 777 /app/BlackPearlBot.py
RUN chmod 777 /app/BlackPearl.txt
RUN chmod 777 /usr/src/app
CMD ["python3", "BlackPearlBot.py"]
