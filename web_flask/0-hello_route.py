#!/usr/bin/python3
""" This script starts a web application that listens
on host 0.0.0.0 and port 5000
"""

from flask import Flask

app = Flask("__name__")


@app.route('/', strict_slashes=False)
def hello():
    """Define an hello message"""
    return ("Hello HBNB!")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=None)
