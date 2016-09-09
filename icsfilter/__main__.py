#!/usr/bin/python3

import os
import logging

import icalendar
import click
import requests

from . import _filters

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('')


def process(cal):
    for f in _filters:
        cal = f(cal)
    return cal

def read_cal(loc):
    if loc.startswith('http'):
        req = requests.get(loc)
        ical = req.text
    else:
        with open(loc) as f:
            ical = f.read()
    cal = icalendar.Calendar.from_ical(ical)
    return cal


@click.group()
@click.option('--filtersdir', default=os.path.expanduser("filtersdir"))
def cli(filtersdir):
    import importlib.util
    for fn in os.listdir(filtersdir):
        if not fn.endswith('.py'):
            continue
        ffn = os.path.join(filtersdir, fn)
        log.info('loading filters from %s' % ffn)
        spec = importlib.util.spec_from_file_location("_filter", ffn)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    log.info('found %i filters' % len(_filters))

@cli.command()
@click.argument('loc')
def dump(loc):
    cal = read_cal(loc)
    cal = process(cal)
    print('%s' % cal.to_ical().decode('utf-8'))

@cli.command()
@click.argument('loc')
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=80)
def serve(loc, host, port):
    import flask

    app = flask.Flask(__name__)

    @app.route('/')
    def slash():
        cal = read_cal(loc)
        cal = process(cal)
        resp = flask.make_response(cal.to_ical().decode('utf-8'))
        resp.headers['Content-Type'] = 'text/calendar'
        return resp

    app.run(host=host, port=port)


if __name__ == '__main__':
    cli()
