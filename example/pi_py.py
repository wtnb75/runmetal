import math
import click
import random
import logging
import time


@click.command()
@click.option("-n", type=int, help="number of samples", default=1000000)
def main(n):
    fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=fmt)
    log = logging.getLogger(__name__)
    c = 0

    log.debug("start %d", n)
    st = time.time()
    for i in range(n):
        x = random.random()
        y = random.random()
        if math.sqrt(x * x + y * y) < 1.0:
            c += 1
    en = time.time() - st
    log.debug("pi: %d/%d = %f, %f sec", c, n, c / n * 4, en)


main()
