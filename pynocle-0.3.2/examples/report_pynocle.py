#!/usr/bin/env python

import os

import report_project


thisdir = os.path.dirname(__file__)


def get_reportproject_args(outdir=None):
    pynocledir = os.path.join(thisdir, '..', 'pynocle')

    import report_project
    runtests = report_project.run_nose(pynocledir)
    return 'Pynocle', pynocledir, outdir, runtests


def main():
    outdir = os.path.join(thisdir, 'exampleoutput')
    args = get_reportproject_args(outdir)
    report_project.report_project(*args)


if __name__ == '__main__':
    main()
