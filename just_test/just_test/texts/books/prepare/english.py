import re


def prepare_prelim(text: str) -> str:
    # Replace multiple whitespaces
    text = re.sub(r'[^\S\n]+', ' ', text)
    # Replace single linebreaks to whitespace
    text = re.sub(r'(\S)[^\S\n]*\n[^\S\n]*(\S)', r'\1 \2', text)

    # Remove underscore
    text = text.replace("_", "")

    # Replace single quotation marks
    # U+2018 Left single quotation mark
    text = text.replace("\u2018", "'")
    # U+2019 Right single quotation mark
    text = text.replace("\u2019", "'")

    # Replace double quotes marks
    # U+201C Left double quotation mark
    text = text.replace("\u201c", '"')
    # U+201D Right double quotation mark
    text = text.replace("\u201d", '"')

    # Remove text in square brackets
    text = re.sub(r'^\s*\[[^[\]\n]*\]\s*', '', text)
    text = re.sub(r'\s*\[[^[\]\n]*\]\s*$', '', text)

    def _sub_square_brackets(m: re.Match) -> str:
        if m.group(1) or m.group(2):
            return ' '
        else:
            return ''

    text = re.sub(r'([^\S\n]*)\[[^[\]\n]*\]([^\S\n]*)', _sub_square_brackets, text)

    # Minimize subsequent whitespaces
    text = re.sub(r'[^\S\n]+', ' ', text)

    return text


def replace_dash_u2014(text: str) -> str:
    """Replace the "U+2014 EM DASH" character."""
    # eve—e—e—ening => evening
    text = re.sub(r'(?i)((\w)\u2014)+\2(\u2014\2)+', r'\g<2>', text)
    # Anita—a => Anita
    text = re.sub(r'(?i)(\w)(\u2014\1)+\b', r'\g<1>', text)
    # A—anita => Anita
    text = re.sub(r'(?i)\b(\w)(\u2014\1)+', r'\g<1>', text)
    # and—oh => and, oh
    text = re.sub(r'(\w)[^\S\r\n]*\u2014[^\S\r\n]*(\w)', r'\g<1>, \g<2>', text)
    # to—", said => to," said
    text = re.sub(r'(\w)\u2014([^\w\s,.:;?!()]{1,2})([,.:;?!]+)([^\S\r\n]\w)', r'\g<1>\g<3>\g<2>\g<4>', text)
    # mean—" continued => mean," continued
    # little—'" and => little,'" and
    text = re.sub(r'(\w)\u2014([^\w\s,.:;?!()]{1,2}[^\S\r\n]\w)', r'\g<1>,\g<2>', text)
    # know—" => know"
    text = re.sub(r'(\w)\u2014([^\w\s,.:;?!()]{1,2}(\s|$))', r'\g<1>\g<2>', text)
    # 'Henrietta'—" resumed => 'Henrietta,'" resumed
    text = re.sub(r'(\w)([^\w\s,.:;?!()])\u2014([^\w\s,.:;?!()][^\S\r\n]\w)', r'\g<1>,\g<2>\g<3>', text)
    # But!—" cried => But!" cried
    text = re.sub(r'(\w[,.:;?!]+)\u2014([^\w\s,.:;?!()]{1,2}(\s|$))', r'\g<1>\g<2>', text)
    # you.—Come => you. Come
    text = re.sub(r'(\w[,.:;?!]+)\u2014(\w)', r'\g<1> \g<2>', text)
    # this:— => this:
    text = re.sub(r'(\w[,.:;?!]+)\u2014(\s|$)', r'\g<1>\g<2>', text)
    # "—change => "change
    text = re.sub(r'((\s|^)[^\w\s,.:;?!()]{1,2})\u2014(\w)', r'\g<1>\g<3>', text)
    # along—"Catch => along, "Catch
    text = re.sub(r'(\w)\u2014([^\w\s,.:;?!()]{1,2}\w)', r'\g<1>, \g<2>', text)
    # the dash is between words, but not before punctuation
    text = re.sub(r'(\w[^\w\r\n]*)\u2014([^\w,.:;?!\r\n]*\w)', r'\g<1> \g<2>', text)
    # in all other cases, remove the dash
    text = text.replace('\u2014', '')

    return text


def replace_double_hyphen(text: str) -> str:
    """Replace the double hyphen separator (--)."""
    # ma--a--a--ad => mad
    text = re.sub(r'(?i)((\w)--)+\2(--\2)+', r'\g<2>', text)
    # cocoa--a => cocoa
    text = re.sub(r'(?i)(\w)(--\1)+\b', r'\g<1>', text)
    # H--hup! => Hup!
    text = re.sub(r'(?i)\b(\w)(--\1)+', r'\g<1>', text)
    # and--well => and, well
    text = re.sub(r'(\w)[^\S\r\n\-]*(?:--){1,2}[^\S\r\n\-]*(\w)', r'\g<1>, \g<2>', text)
    # but--" he => but," he
    text = re.sub(r'(\w)(?:--){1,2}([^\w\s,.:;?!()\-]{1,2}[^\S\r\n]\w)', r'\g<1>,\g<2>', text)
    # that--" => that"
    text = re.sub(r'(\w)(?:--){1,2}([^\w\s,.:;?!()\-]{1,2}(\s|$))', r'\g<1>\g<2>', text)
    # oh!--" => oh!"
    text = re.sub(r'(\w[,.:;?!]+)(?:--){1,2}([^\w\s,.:;?!()\-]{1,2}(\s|$))', r'\g<1>\g<2>', text)
    # etc.--but => etc. but
    text = re.sub(r'(\w[,.:;?!]+)(?:--){1,2}(\w)', r'\g<1> \g<2>', text)
    # said:-- => said:
    text = re.sub(r'(\w[,.:;?!]+)(?:--){1,2}(\s|$)', r'\g<1>\g<2>', text)
    # "--not => "not
    text = re.sub(r'((\s|^)[^\w\s,.:;?!()\-]{1,2})(?:--){1,2}(\w)', r'\g<1>\g<3>', text)
    # commented--"and => commented, "and
    text = re.sub(r'(\w)(?:--){1,2}([^\w\s,.:;?!()\-]{1,2}\w)', r'\g<1>, \g<2>', text)
    # the dash is between words, but not before punctuation
    text = re.sub(r'(\w[^\w\r\n\-]*)(?:--){1,2}([^\w,.:;?!\r\n\-]*\w)', r'\g<1> \g<2>', text)
    # in all other cases, remove the separator
    text = re.sub(r'([^\-]|^)(?:--){1,2}([^\-]|$)', r'\g<1>\g<2>', text)

    return text


def remove_parentheses(text: str) -> str:
    """Remove parentheses from the text."""
    # (Beginning => Beginning
    text = re.sub(r'(^|\n\s*\n)(\W*)\(', r'\g<1>\g<2>', text)
    # ending) => ending
    text = re.sub(r'\)(\W*)($|\n\s*\n)', r'\g<1>\g<2>', text)
    # mind (as => mind, as
    text = re.sub(r'(\w)([^\S\n]+)\(([^\w\s,.:;?!()]{0,2}\w)', r'\g<1>,\g<2>\g<3>', text)
    # prepare) your => prepare, your
    text = re.sub(r'(\w)\)([^\S\n]+\w)', r'\g<1>,\g<2>', text)
    # think" (for => think," for
    text = re.sub(r'(\w)([^\w\s,.:;?!()]{1,2}[^\S\n]+)\(([^\w\s,.:;?!()]{0,2}\w)', r'\g<1>,\g<2>\g<3>', text)
    # over) "yes => over, "yes
    text = re.sub(r'(\w)\)([^\S\n]+[^\w\s,.:;?!()]{1,2}\w)', r'\g<1>,\g<2>', text)
    # it?), and => it? and
    text = re.sub(r'(\w[,.:;?!]+[^\w\s,.:;?!()]{0,2})\)[,.:;?!]+([^\S\n]+\w)', r'\g<1>\g<2>', text)
    # space after the closing parenthesis but before the letter
    # it), and => it, and
    text = re.sub(r'\)([^\w\s()]*[^\S\n]+)', r'\g<1>', text)
    # space after the letter but before the opening parenthesis
    # wig, (look
    text = re.sub(r'([^\S\n]+[^\w\s()]*)\(', r'\g<1>', text)
    # remove the rest of the parentheses, replacing them with a space
    text = re.sub(r'[()]+', ' ', text)

    return text


def prepare_english_book_text(text: str) -> str:
    text = prepare_prelim(text)

    # Replace the "U+2014 EM DASH" character
    text = replace_dash_u2014(text)

    # Replace the double hyphen separator (--)
    text = replace_double_hyphen(text)

    text = remove_parentheses(text)

    return text
