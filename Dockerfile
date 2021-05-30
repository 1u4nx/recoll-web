FROM docker.io/debian
MAINTAINER lu4nx <lx@shellcodes.org>

RUN echo -n 'deb http://mirrors.tuna.tsinghua.edu.cn/debian/ buster main contrib non-free\ndeb http://mirrors.tuna.tsinghua.edu.cn/debian/ buster-updates main contrib non-free\ndeb http://mirrors.tuna.tsinghua.edu.cn/debian/ buster-backports main contrib non-free\ndeb http://mirrors.tuna.tsinghua.edu.cn/debian-security buster/updates main contrib non-free' > /etc/apt/sources.list
RUN apt update -y
RUN apt install -y python3 python3-pip recollcmd

RUN mkdir -p ~/.recoll && echo 'topdirs = /home/app/static/doc' > ~/.recoll/recoll.conf

COPY requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt -i http://pypi.doubanio.com/simple --trusted-host pypi.doubanio.com

VOLUME ["/home/app"]
WORKDIR /home/app

EXPOSE 80
CMD gunicorn -w 4 recoll_web:app -b 0.0.0.0:80
