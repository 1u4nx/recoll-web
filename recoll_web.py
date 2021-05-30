# coding=utf-8

import subprocess
from os import system
from os.path import basename
from recoll import recoll
from flask import Flask, request, render_template

app = Flask(__name__)

try:
    db = recoll.connect()
    query = db.query()
except OSError:
    system("recollindex")


class HighLight(object):
    def startMatch(self, idx):
        # HTML 代码直接渲染模板有安全风险，暂不考虑用 HTML 高亮
        # return '<span class="search-result-highlight">'
        return ""

    def endMatch(self):
        # return '</span>'
        return ""


@app.route("/")
def home():
    keyword = request.args.get("q", None)
    page = request.args.get("page", "1")
    # 默认1页20条记录
    per_page_max = 20

    if not keyword:
        return render_template("index.html", page=0)

    try:
        page = int(page)
    except ValueError:
        return "`page` error, please give a integer."

    offset = (page - 1) * per_page_max
    try:
        doc_total = query.execute(keyword, fetchtext=True)
    except ValueError as err:
        return str(err)

    rowcount = query.rowcount

    if rowcount < per_page_max:
        per_page_max = rowcount

    if rowcount > 0:
        if type(query.next) == int:
            query.next = offset
        else:
            try:
                query.scroll(offset, mode="absolute")
            except IndexError:
                return "not found."

    try:
        search_results = query.fetchmany(per_page_max)
    except AttributeError:
        return render_template("index.html",
                               doc_total=0,
                               keyword=keyword,
                               page=0)

    if not search_results:
        return render_template("index.html",
                               doc_total=0,
                               keyword=keyword,
                               page=0)

    highlight_handler = HighLight()

    page_total = int(doc_total / per_page_max)

    for _ in search_results:
        _.url = basename(_.url)
        _.download_url = f"/static/doc/{_.url}"
        _.snippet = query.makedocabstract(_, highlight_handler)

    return render_template("index.html",
                           doc_total=doc_total,
                           page=page,
                           page_total=page_total,
                           keyword=keyword,
                           per_page_max=per_page_max,
                           search_results=search_results)


@app.route("/update_index")
def get():
    subprocess.Popen(["recollindex"])
    return "update index..."


if __name__ == '__main__':
    app.run(port=7000)
