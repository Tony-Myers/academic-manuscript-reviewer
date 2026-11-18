# Third-party components

## PDF.js

The local viewer bundles pdfjs-dist 6.5.438, legacy build, from the existing working
viewer. See `app/vendor/pdfjs/VERSION.txt` for the package tarball digest and
`app/vendor/pdfjs/LICENSE` for Apache-2.0. Scripting/QuickJS is not bundled.
Upstream: https://github.com/mozilla/pdf.js and https://github.com/mozilla/pdfjs-dist.
No claim is made that all files in the directory use the same licence.

Preserved component notices:

- `cmaps/LICENSE`: Adobe character-map redistribution terms.
- `iccs/LICENSE`: CC0 ICC profile.
- `standard_fonts/LICENSE_FOXIT`: PDFium/Foxit font redistribution terms.
- `standard_fonts/LICENSE_LIBERATION`: Liberation 1.07.4 GPLv2 with font exceptions.
- `wasm/LICENSE_JBIG2`, `LICENSE_QCMS`, `LICENSE_OPENJPEG` and their
  `LICENSE_PDFJS_*` wrappers: the respective PDFium, Mozilla and OpenJPEG terms.

Keep all notices and copyright attribution with copies. The font embedding
exception is not a replacement licence for the font binaries themselves.

## Liberation corresponding source

The four unchanged LiberationSans TTF assets identify version 1.07.4. Upstream
explains that version 1 uses GPLv2 with exceptions; later OFL versions must not
be substituted as the licence for these binaries.

The upstream 1.07.4 font sources, including SFDs, build scripts,
Makefile, notices and README, is supplied under `third_party/liberation-1.07.4/`.
The optional upstream icon artwork is omitted; it is not needed by the font build.
The font build is not executed by the application. Font rebuilding requires the upstream
FontForge build environment. Binaries were not rebuilt during release preparation.

Source repository: https://github.com/liberationfonts/liberation-1.7-fonts
Source revision: dbeb786b4ede1eaec2ec5cb8d3b75d21641e2a35 (1.07.4 release).
Upstream PDF.js licence correction: https://github.com/mozilla/pdf.js/issues/21746.
Preserve the source/build material and GPL/exception notices on redistribution.

## Python dependencies

Installed independently through pip; their distribution licences/notices remain
in those packages. The application does not vendor them. The release's tested
runtime dependency metadata is listed in DEPENDENCIES.md. In particular pypdf
uses BSD-3-Clause; pypdfium2 carries BSD-3-Clause, Apache-2.0 and PDFium/dependency
notices. Packaging installed binaries later requires retaining those notices too.
