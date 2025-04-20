import typing as t
from contextlib import contextmanager
from gettext import gettext as _

from ._compat import term_len
from .parser import split_opt


FORCED_WIDTH: t.Optional[int] = None


def measure_table(rows: t.Iterable[t.Tuple[str, str]]) -> t.Tuple[int, ...]:
    widths: t.Dict[int, int] = {}

    for row in rows:
        for idx, col in enumerate(row):
            widths[idx] = max(widths.get(idx, 0), term_len(col))

    return tuple(y for x, y in sorted(widths.items()))


def iter_rows(
    rows: t.Iterable[t.Tuple[str, str]], col_count: int
) -> t.Iterator[t.Tuple[str, ...]]:
    for row in rows:
        yield row + ("",) * (col_count - len(row))


def wrap_text(
    text: str,
    width: int = 78,
    initial_indent: str = "",
    subsequent_indent: str = "",
    preserve_paragraphs: bool = False,
) -> str:
    
    from ._textwrap import TextWrapper

    text = text.expandtabs()
    wrapper = TextWrapper(
        width,
        initial_indent=initial_indent,
        subsequent_indent=subsequent_indent,
        replace_whitespace=False,
    )
    if not preserve_paragraphs:
        return wrapper.fill(text)

    p: t.List[t.Tuple[int, bool, str]] = []
    buf: t.List[str] = []
    indent = None

    def _flush_par() -> None:
        if not buf:
            return
        if buf[0].strip() == "\b":
            p.append((indent or 0, True, "\n".join(buf[1:])))
        else:
            p.append((indent or 0, False, " ".join(buf)))
        del buf[:]

    for line in text.splitlines():
        if not line:
            _flush_par()
            indent = None
        else:
            if indent is None:
                orig_len = term_len(line)
                line = line.lstrip()
                indent = orig_len - term_len(line)
            buf.append(line)
    _flush_par()

    rv = []
    for indent, raw, text in p:
        with wrapper.extra_indent(" " * indent):
            if raw:
                rv.append(wrapper.indent_only(text))
            else:
                rv.append(wrapper.fill(text))

    return "\n\n".join(rv)


class HelpFormatter:
    

    def __init__(
        self,
        indent_increment: int = 2,
        width: t.Optional[int] = None,
        max_width: t.Optional[int] = None,
    ) -> None:
        import shutil

        self.indent_increment = indent_increment
        if max_width is None:
            max_width = 80
        if width is None:
            width = FORCED_WIDTH
            if width is None:
                width = max(min(shutil.get_terminal_size().columns, max_width) - 2, 50)
        self.width = width
        self.current_indent = 0
        self.buffer: t.List[str] = []

    def write(self, string: str) -> None:
        
        self.buffer.append(string)

    def indent(self) -> None:
        
        self.current_indent += self.indent_increment

    def dedent(self) -> None:
        
        self.current_indent -= self.indent_increment

    def write_usage(
        self, prog: str, args: str = "", prefix: t.Optional[str] = None
    ) -> None:
        
        if prefix is None:
            prefix = f"{_('Usage:')} "

        usage_prefix = f"{prefix:>{self.current_indent}}{prog} "
        text_width = self.width - self.current_indent

        if text_width >= (term_len(usage_prefix) + 20):
            
            indent = " " * term_len(usage_prefix)
            self.write(
                wrap_text(
                    args,
                    text_width,
                    initial_indent=usage_prefix,
                    subsequent_indent=indent,
                )
            )
        else:
            
            self.write(usage_prefix)
            self.write("\n")
            indent = " " * (max(self.current_indent, term_len(prefix)) + 4)
            self.write(
                wrap_text(
                    args, text_width, initial_indent=indent, subsequent_indent=indent
                )
            )

        self.write("\n")

    def write_heading(self, heading: str) -> None:
        
        self.write(f"{'':>{self.current_indent}}{heading}:\n")

    def write_paragraph(self) -> None:
        
        if self.buffer:
            self.write("\n")

    def write_text(self, text: str) -> None:
        
        indent = " " * self.current_indent
        self.write(
            wrap_text(
                text,
                self.width,
                initial_indent=indent,
                subsequent_indent=indent,
                preserve_paragraphs=True,
            )
        )
        self.write("\n")

    def write_dl(
        self,
        rows: t.Sequence[t.Tuple[str, str]],
        col_max: int = 30,
        col_spacing: int = 2,
    ) -> None:
        
        rows = list(rows)
        widths = measure_table(rows)
        if len(widths) != 2:
            raise TypeError("Expected two columns for definition list")

        first_col = min(widths[0], col_max) + col_spacing

        for first, second in iter_rows(rows, len(widths)):
            self.write(f"{'':>{self.current_indent}}{first}")
            if not second:
                self.write("\n")
                continue
            if term_len(first) <= first_col - col_spacing:
                self.write(" " * (first_col - term_len(first)))
            else:
                self.write("\n")
                self.write(" " * (first_col + self.current_indent))

            text_width = max(self.width - first_col - 2, 10)
            wrapped_text = wrap_text(second, text_width, preserve_paragraphs=True)
            lines = wrapped_text.splitlines()

            if lines:
                self.write(f"{lines[0]}\n")

                for line in lines[1:]:
                    self.write(f"{'':>{first_col + self.current_indent}}{line}\n")
            else:
                self.write("\n")

    @contextmanager
    def section(self, name: str) -> t.Iterator[None]:
        
        self.write_paragraph()
        self.write_heading(name)
        self.indent()
        try:
            yield
        finally:
            self.dedent()

    @contextmanager
    def indentation(self) -> t.Iterator[None]:
        
        self.indent()
        try:
            yield
        finally:
            self.dedent()

    def getvalue(self) -> str:
        
        return "".join(self.buffer)


def join_options(options: t.Sequence[str]) -> t.Tuple[str, bool]:
    
    rv = []
    any_prefix_is_slash = False

    for opt in options:
        prefix = split_opt(opt)[0]

        if prefix == "/":
            any_prefix_is_slash = True

        rv.append((len(prefix), opt))

    rv.sort(key=lambda x: x[0])
    return ", ".join(x[1] for x in rv), any_prefix_is_slash
