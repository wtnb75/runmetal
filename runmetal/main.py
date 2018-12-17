import os
import math
import logging
import numpy
import click
import yaml
import time
from jinja2 import Environment

from .pymetal import PyMetal

log = None

# from nslogger import NSHandler
# fmt = "%(levelname)s %(name)s %(message)s"
# logging.basicConfig(level=logging.DEBUG, handlers=[NSHandler()], format=fmt)

# fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
# logging.basicConfig(level=logging.DEBUG, format=fmt)
# log = logging.getLogger(__name__)


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


def apply_template(s, vars: dict):
    if isinstance(s, str):
        env = Environment()
        res = env.from_string(s).render(vars)
        # log.debug("res: %s...%s", type(res), res)
        if res == s:
            # log.debug("not changed")
            return s
        try:
            # result is integer?
            return int(res)
        except ValueError:
            pass
        try:
            # result is float?
            return float(res)
        except ValueError:
            # log.debug("is str")
            return res
    elif isinstance(s, dict):
        res = {}
        for k, v in s.items():
            res[k] = apply_template(v, vars)
        return res
    elif isinstance(s, (tuple, list)):
        return [apply_template(x, vars) for x in s]
    return s


def read_source(basedir: str, p: dict) -> str:
    srcstr = p.get("source", None)
    if srcstr is not None:
        return srcstr
    fn = p.get("filename", None)
    if fn is not None:
        return open(os.path.join(basedir, fn)).read()
    log.error("source or filename not found: %s", p)
    raise Exception("source or filename not found: %s" % (p,))


def loadvalue(basedir: str, fn: str, format: str = 'numpy') -> numpy.ndarray:
    if format == 'numpy':
        return numpy.load(os.path.join(basedir, fn))
    else:
        raise Exception("not implemented format to load: %s" % (format))


def savevalue(basedir: str, fn: str, val: numpy.ndarray, format: str = 'numpy'):
    if format == 'numpy':
        return numpy.save(os.path.join(basedir, fn), val)
    else:
        raise Exception("not implemented format to save: %s" % (format))


def str2num(s):
    if isinstance(s, (list, tuple)):
        return [str2num(x) for x in s]
    if not isinstance(s, str):
        return s
    sfxmap = {
        'k': 1000,
        'm': 1000**2,
        'g': 1000**3,
        't': 1000**4,
        'p': 1000**5,
        'e': 1000**6,
        'z': 1000**7,
        'y': 1000**8,
        'K': 1024,
        'M': 1024**2,
        'G': 1024**3,
        'T': 1024**4,
        'P': 1024**5,
        'E': 1024**6,
        'Z': 1024**7,
        'Y': 1024**8,
    }
    m = 1
    for k, v in sfxmap.items():
        if s.endswith(k):
            m = v
            s = s[:-1]
    return int(s) * m


def isnewer(f1, f2):
    if not os.path.exists(f1):
        return True
    if not os.path.exists(f2):
        return False
    return os.path.getmtime(f1) < os.path.getmtime(f2)


def setup_log(verbose):
    global log
    logfmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format=logfmt)
    else:
        logging.basicConfig(level=logging.INFO, format=logfmt)
    log = logging.getLogger(__name__)


@cli.command()
@click.argument('input', type=click.Path(exists=True))
@click.option('--verbose/--no-verbose', default=False)
@click.option('--make/--no-make', default=False)
@click.option('--extra', '-e', multiple=True)
def run(input, verbose, make, extra):
    setup_log(verbose)
    pm = PyMetal()
    src = []
    data = yaml.load(open(input))
    vars = data.get("vars", {})
    for ev in extra:
        k, v = ev.split("=", 1)
        vars[k] = v
    basedir = os.path.dirname(input)
    # log.debug("data: %s", data)
    funcs = {}
    bufs = {}
    pm.opendevice()
    log.debug("dev: %s", pm.dev.name())
    progs = apply_template(data.get("program", []), vars)
    if isinstance(progs, str):
        if progs == "default":
            pm.openlibrary_default()
        else:
            pm.openlibrary_compiled(os.path.join(basedir, str))
    else:
        base, ext = os.path.splitext(input)
        libfn = base + ".metallib"
        if make and len(extra) == 0 and isnewer(input, libfn):
            pm.openlibrary_compiled(libfn)
        else:
            src = []
            for p in progs:
                src.append(read_source(basedir, p))
            pm.openlibrary("\n".join(src))
    # log.debug("lib: %s", pm.lib)
    for f in apply_template(data.get("entrypoint", []), vars):
        nm = f.get("name", None)
        if nm is None:
            log.error("no name(ep): %s", f)
            continue
        funcs[nm] = pm.getfn(nm)
    for b in apply_template(data.get("buffer", []), vars):
        nm = b.get("name", None)
        if nm is None:
            log.error("no name(buf): %s", b)
            continue
        # TODO: if type is texture...
        load = b.get("load", None)
        if load is not None:
            npdata = loadvalue(basedir, load)
            bufs[nm] = pm.numpybuffer(npdata, label=nm)
            continue
        sz = str2num(b.get("size", None))
        if sz is None:
            log.error("no size: %s", b)
            continue
        dtype = b.get("dtype", "float32")
        dtypex = getattr(numpy, dtype)
        mode = b.get("mode", "zero")
        log.debug("initialize %s buffer: %d, %s", mode, sz, dtype)
        if mode == "zero":
            bufs[nm] = pm.emptybuffer(sz * dtypex().itemsize, label=nm)
        elif mode in ("random", "ranf"):
            npdata = dtypex(getattr(numpy.random, mode)(sz))
            bufs[nm] = pm.numpybuffer(npdata, label=nm)
        elif mode in ("irandom"):
            iinfo = numpy.iinfo(dtypex)
            npdata = numpy.random.randint(
                iinfo.min, iinfo.max, size=sz, dtype=dtypex)
            bufs[nm] = pm.numpybuffer(npdata, label=nm)
        else:
            log.error("unknown mode: %s", b)
            continue
        log.debug("done")
    cq, cb = pm.getqueue()
    for prog in apply_template(data.get("progn", []), vars):
        typ = prog.get("type", "compute")
        name = prog.get("name", None)
        descr = prog.get("description", None)
        if name is not None or descr is not None:
            log.info("process %s: %s", name, descr)
        if typ == "compute":
            fn = prog.get("entrypoint", None)
            if fn is None:
                log.error("no entrypoint: %s", prog)
                continue
            if fn not in funcs:
                log.info("no function named %s? reload", fn)
                funcs[fn] = pm.getfn(fn)
            if funcs[fn] is None:
                log.error("no function named %s", fn)
                continue
            bufargs = []
            for i, b in enumerate(prog.get("buffers", [])):
                bufargs.append(bufs[b])
            threadargs = prog.get("options", {}).get("threads", None)
            iterations = str2num(
                prog.get("options", {}).get("iterations", None))
            pm.enqueue_compute(
                cb, funcs[fn], bufargs, threadargs, iterations, label=name)
        elif typ == "render":
            # TBD
            log.error("type %s: not implemented yet", typ)
        elif typ == "blit":
            for i, b in enumerate(prog.get("buffers", [])):
                pm.enqueue_blit(cb, bufs[b], label="%s%d" % (name, i))
    log.info("commit")
    pm.start_process(cb)
    log.info("wait")
    start = time.time()
    pm.wait_process(cb)
    log.info("done %g sec", time.time() - start)
    for o in apply_template(data.get("result", []), vars):
        bufname = o.get("buffer", None)
        if bufname is None or bufname not in bufs:
            log.error("buffer not found: %s", o)
            continue
        ofn = o.get("output", None)
        if ofn is None:
            log.error("output not found: %s", o)
            continue
        buf = bufs[bufname]
        # log.debug("buffer: %s", buf)
        typ = o.get("dtype", "float32")
        if not hasattr(numpy, typ):
            log.error("no such type: %s", o)
            continue
        npbuf = pm.buf2numpy(buf, dtype=getattr(numpy, typ))
        log.debug("%s", npbuf)
        savevalue(basedir, ofn, npbuf)
    for o in apply_template(data.get("post-process", []), vars):
        script = read_source(basedir, o)
        name = o.get("name")
        args = {
            "log": logging.getLogger(name),
            "numpy": numpy,
            "math": math,
        }
        for b in o.get("buffers", []):
            name = b.get("name")
            typ = b.get("dtype", "float32")
            args[name] = pm.buf2numpy(bufs[name], dtype=getattr(numpy, typ))
        if name is not None:
            log.info("run post-process %s", name)
        log.debug("script: %s", script)
        log.debug("args: %s", list(args.keys()))
        exec(script, args)
        log.debug("finished")


@cli.command()
@click.option('--name', default=None)
def mtlinfo(name):
    pm = PyMetal()
    pm.opendevice(name)
    print("\n".join(pm.device2str(pm.dev)))


@cli.command()
def lsdev():
    pm = PyMetal()
    for d in pm.lsdev():
        print(d.name())


@cli.command()
@click.argument('input', type=click.Path(exists=True))
@click.option('--verbose/--no-verbose', default=False)
@click.option('--make/--no-make', default=False)
def compile(input, verbose, make):
    setup_log(verbose)
    data = yaml.load(open(input))
    vars = data.get("vars", {})
    basedir = os.path.dirname(input)
    bn, ext = os.path.splitext(os.path.basename(input))
    outfn = os.path.join(basedir, bn + ".metallib")
    if not make or not isnewer(input, outfn):
        src = []
        for p in apply_template(data.get("program", []), vars):
            src.append(read_source(basedir, p))
        pm = PyMetal()
        log.debug("source: %s", src)
        pm.compile("\n".join(src), outfn)


if __name__ == '__main__':
    cli()
