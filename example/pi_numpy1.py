import numpy
import logging
import click


@click.command()
@click.option("-n", type=int, help="number of samples", default=1000000)
def main(n):
    fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=fmt)
    log = logging.getLogger(__name__)

    log.debug("generate random data: %d", n)
    data = numpy.float32(numpy.random.random(n * 2))
    data.shape = (n, 2)
    log.debug("calculate distance")
    output = numpy.apply_along_axis(
        lambda x: numpy.sqrt(numpy.sum(x * x)) < 1.0, 1, data)
    log.debug("show result")
    print("pi=%f" % (numpy.sum(output == True) / len(output) * 4))
    log.debug("finished")


main()
