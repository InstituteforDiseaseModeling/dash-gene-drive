from Gene_Drive import app

server = app.app.server
if __name__ == '__main__':
    app.app.run_server(debug=False,
                   port=80,
                   host='0.0.0.0')