# containership.io

Gluu's containership.io application

## Images

Each image is stored under its own directory.
Directories prefixed by `_` marked as unsupported/deprecated images.

## Versioning/Tagging

Each image uses their own versioning/tagging format.

    <IMAGE-NAME>:<GLUU-SERVER-VERSION>_<INTERNAL-REV-VERSION>

For example, `gluufederation/oxauth:3.0.1_rev1.0.0` consists of:

- glufederation/oxauth as `<IMAGE_NAME>`; the actual image name
- 3.0.1 as `GLUU-SERVER-VERSION`; the Gluu Server version as setup reference
- rev1.0.0 as `<INTERNAL-REV-VERSION>`; revision made when developing the image

See `CHANGES.md` under each directory to see its version and changelog.
