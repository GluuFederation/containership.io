import tempfile
from subprocess import Popen
from subprocess import PIPE


def po_run(cmd_str, raise_error=True):
    cmd_list = cmd_str.strip().split()

    try:
        p = Popen(cmd_list, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        error_code = p.returncode

        if raise_error and error_code:
            raise RuntimeError("return code {}: {}".format(error_code, stderr.strip()))
        return stdout.strip(), stderr.strip(), error_code
    except OSError as exc:
        raise RuntimeError("return code {}: {}".format(exc.errno, exc.strerror))


def render_template(src, dest, ctx=None):
        """Renders non-jinja template.

        :param src: Relative path to template.
        :param ctx: Context that will be populated into template.
        :returns: String of rendered template.
        """
        ctx = ctx or {}
        file_basename = os.path.basename(src)
        local = os.path.join(tempfile.mkdtemp(), file_basename)

        with open(src, "r") as fp:
            rendered_content = fp.read() % ctx

        with open(local, "w") as fp:
            fp.write(rendered_content)

        shutil.copyfile(local, dest)
