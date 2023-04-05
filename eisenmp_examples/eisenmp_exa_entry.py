# Python 3 server example
# https://pythonbasics.org/webserver/
# mod by 44xtc44

import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import eisenmp_examples

hostName = "localhost"
serverPort = 12_321


class Menu:

    example_menu = [
        '[single shot] Multiple Flask server in each processes - share a DB',
        '[single shot] One Flask server on Every process - share a DB',
        'Prime Number calculation',
        'Web CSV large list calculation',
        'One simple http server presents a radio on every process',
        'Two Queues fed at once',
        'Brute force attack with dictionary and itertools generator',
    ]

    exa_tpl_lst = [
        (0, example_menu[0], eisenmp_examples.eisenmp_exa_multi_srv_each_cpu.main),
        (1, example_menu[1], eisenmp_examples.eisenmp_exa_each_flask_orm_srv_one_cpu.main),
        (2, example_menu[2], eisenmp_examples.eisenmp_exa_prime.main),
        (3, example_menu[3], eisenmp_examples.eisenmp_exa_web_csv.main),
        (4, example_menu[4], eisenmp_examples.eisenmp_exa_http.main),
        (5, example_menu[5], eisenmp_examples.eisenmp_exa_double_q.main),
        (6, example_menu[6], eisenmp_examples.eisenmp_exa_bruteforce.main)
    ]


def run_http():
    """Blocked, no loop here
    """
    global serverPort

    while 1:
        try:
            webServer = HTTPServer((hostName, serverPort), MyServer)
            break
        except OSError:
            print(f'serverPort in use {serverPort}\n\tadd one to port number')
            serverPort += 1  # port already in use

    print(f"Examples http://%s:%s" % (hostName, serverPort))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print("Server stopped.")


class MyServer(BaseHTTPRequestHandler):

    def do_POST(self):
        """"""
        # print(self.headers)
        length = int(self.headers.get_all('content-length')[0])
        print(self.headers.get_all('content-length'))
        data_string = self.rfile.read(length)
        example_fun = Menu.exa_tpl_lst[int(data_string)][2]
        example_fun()
        print(data_string)
        self.send_response(200)
        # self.send_header("Content-type", "text/plain")
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.flush_headers()
        json_string = json.dumps(str(data_string))  # just for the sake of my art
        self.wfile.write(bytes(json_string, "utf-8"))

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        center = "text-align:center;"
        brown = "color:brown;font-family:Roboto;"
        black = "color:black;font-family:Roboto;font-weight:700;"
        flex_outer = "display: flex;color:brown;font-family:Roboto;font-weight:600;"
        flex_mid = "display: flex;flex-direction: column;margin: auto;"

        da_html_lst = [
            "<!doctype html><html><head>",
            "<meta charset='utf-8'>",
            "<meta name='viewport' content='width=device-width initial-scale=1, shrink-to-fit=no'/>",
            # "<link rel=stylesheet href=https://fonts.googleapis.com/css?family=Roboto/>",
            f"<title>https://pythonbasics.org</title></head>",
            "<body>",
            f"<h1 style={center}{brown}'> Welcome to eisenmp_examples</h1>",
            f"<p style={center}{black}'> buttons marked [single shot] run alone - else blocks or crash </p>",
            f"<div class='container' style='{flex_outer}'>",
            f"<div class='middle' style='{flex_mid}'>",

            'example_btn',

            "</div></div>",
            "Path: <p id=pRspReturn> </p>",
            "</body></html>",
            "<script>",
            "function getExa(radio_btn_id) {",
            "const xhr = new XMLHttpRequest();",
            "xhr.open('POST', '/');",
            "xhr.onload = function () {console.log('xhr r ', xhr.response);}; ",
            "xhr.send(radio_btn_id);",
            "let pRspReturn = document.getElementById('pRspReturn');",
            "pRspReturn.innerText=radio_btn_id;",
            "}",
            "</script>",
            "</body></html>"
        ]

        for _ in da_html_lst:
            if _ == 'example_btn':
                for i, _ in enumerate(Menu.exa_tpl_lst):
                    idx = Menu.exa_tpl_lst[i][0]
                    show = Menu.exa_tpl_lst[i][1]
                    exa_html_line = f"<div><label><input type='radio' name='da'" \
                                    f"id='{idx}' onclick='getExa(id)'>{show}</label></div>"
                    self.wfile.write(bytes(exa_html_line, "utf-8"))
                continue
            self.wfile.write(bytes(_, "utf-8"))


def main():
    """
    """
    start = time.perf_counter()

    run_http()

    print('Time in sec: ', round((time.perf_counter() - start)))


if __name__ == '__main__':
    main()
