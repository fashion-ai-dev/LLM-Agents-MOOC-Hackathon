import json
import ast
import re

# to be used by ALL TOOLS ALWAYS
def parse_tool_output(output):
  # Initialize output_dict as an empty dictionary by default
  output_dict = {}

  # Check if the output is a string
  if isinstance(output, str):
    try:
      # Attempt to parse the string as JSON
      output_dict = json.loads(output)
    except json.JSONDecodeError:
      try:
        # If JSON parsing fails, try using ast.literal_eval for Python-like dict strings
        output_dict = ast.literal_eval(output)
      except (ValueError, SyntaxError) as e:
        # If parsing fails, raise an error instead of returning an empty dictionary
                raise ValueError(f"Failed to parse output: {e}")
  elif isinstance(output, dict):
    # If the output is already a dictionary, use it directly
    output_dict = output

  # Return a dict
  return output_dict

import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def parse_sanitize_tool_output(output, sanitize=True):
    """
    Parses the tool output, handling JSON, Python-like dictionaries, and sanitization.
    If the output is already a dictionary, it is returned as-is.
    
    :param output: The input to parse (can be string, dictionary, or similar).
    :param sanitize: Whether to apply string sanitization for JSON-like strings.
    :return: Parsed dictionary.
    """
    # If the output is already a dictionary, return it directly
    if isinstance(output, dict):
        # logger.debug("Output is already a dictionary.")
        return output

    # Function to sanitize JSON-like strings
    def sanitize_string(s):
        # logger.debug("Sanitizing string.")
        # Replace improperly escaped quotes
        s = s.replace("\\'", "'")  # Fix escaped single quotes
        # Replace unescaped single quotes with double quotes, but only outside existing double quotes
        s = re.sub(r"(?<!\\)'(?=(?:[^\"\\\\]*\\\\.)*[^\"\\\\]*$)", '"', s)
        # Remove trailing commas (common JSON issue)
        s = re.sub(r",(?=\s*[\]}])", "", s)
        # Handle missing commas between key-value pairs
        s = re.sub(r"(\w+)(\s*:\s*)", r'"\1"\2', s)  # Ensure keys are quoted
        return s

    try:
        # Check if the output is a string
        if isinstance(output, str):
            # logger.debug("Output is a string. Attempting to parse.")
            try:
                # First attempt: Parse as JSON
                return json.loads(output)
            except json.JSONDecodeError as e:
                # logger.debug(f"JSON parsing failed: {e}")
                if sanitize:
                    # Sanitize the string and try parsing again
                    # logger.debug("Sanitizing output and retrying JSON parsing.")
                    sanitized_output = sanitize_string(output)
                    return json.loads(sanitized_output)
                else:
                    raise

        # Attempt parsing as Python-like dictionary
        # logger.debug("Trying to parse using ast.literal_eval.")
        return ast.literal_eval(output)
    except (json.JSONDecodeError, ValueError, SyntaxError) as e:
        logger.error(f"Failed to parse the output: {e}")
        raise ValueError(f"Failed to parse the output: {e}")



def quote_plus(string, safe='', encoding=None, errors=None):
    """Like quote(), but also replace ' ' with '+', as required for quoting
    HTML form values. Plus signs in the original string are escaped unless
    they are included in safe. It also does not have safe default to '/'.
    """
    # Check if ' ' in string, where string may either be a str or bytes.  If
    # there are no spaces, the regular quote will produce the right answer.
    if ((isinstance(string, str) and ' ' not in string) or
        (isinstance(string, bytes) and b' ' not in string)):
        return quote(string, safe, encoding, errors)
    if isinstance(safe, str):
        space = ' '
    else:
        space = b' '
    string = quote(string, safe + space, encoding, errors)
    return string.replace(' ', '+')



def urlencode(query, doseq=False, safe='', encoding=None, errors=None,
              quote_via=quote_plus):
    """Encode a dict or sequence of two-element tuples into a URL query string.

    If any values in the query arg are sequences and doseq is true, each
    sequence element is converted to a separate parameter.

    If the query arg is a sequence of two-element tuples, the order of the
    parameters in the output will match the order of parameters in the
    input.

    The components of a query arg may each be either a string or a bytes type.

    The safe, encoding, and errors parameters are passed down to the function
    specified by quote_via (encoding and errors only if a component is a str).
    """

    if hasattr(query, "items"):
        query = query.items()
    else:
        # It's a bother at times that strings and string-like objects are
        # sequences.
        try:
            # non-sequence items should not work with len()
            # non-empty strings will fail this
            if len(query) and not isinstance(query[0], tuple):
                raise TypeError
            # Zero-length sequences of all types will get here and succeed,
            # but that's a minor nit.  Since the original implementation
            # allowed empty dicts that type of behavior probably should be
            # preserved for consistency
        except TypeError:
            ty, va, tb = sys.exc_info()
            raise TypeError("not a valid non-string sequence "
                            "or mapping object").with_traceback(tb)

    l = []
    if not doseq:
        for k, v in query:
            if isinstance(k, bytes):
                k = quote_via(k, safe)
            else:
                k = quote_via(str(k), safe, encoding, errors)

            if isinstance(v, bytes):
                v = quote_via(v, safe)
            else:
                v = quote_via(str(v), safe, encoding, errors)
            l.append(k + '=' + v)
    else:
        for k, v in query:
            if isinstance(k, bytes):
                k = quote_via(k, safe)
            else:
                k = quote_via(str(k), safe, encoding, errors)

            if isinstance(v, bytes):
                v = quote_via(v, safe)
                l.append(k + '=' + v)
            elif isinstance(v, str):
                v = quote_via(v, safe, encoding, errors)
                l.append(k + '=' + v)
            else:
                try:
                    # Is this a sufficient test for sequence-ness?
                    x = len(v)
                except TypeError:
                    # not a sequence
                    v = quote_via(str(v), safe, encoding, errors)
                    l.append(k + '=' + v)
                else:
                    # loop over the sequence
                    for elt in v:
                        if isinstance(elt, bytes):
                            elt = quote_via(elt, safe)
                        else:
                            elt = quote_via(str(elt), safe, encoding, errors)
                        l.append(k + '=' + elt)
    return '&'.join(l)


def to_bytes(url):
    warnings.warn("urllib.parse.to_bytes() is deprecated as of 3.8",
                  DeprecationWarning, stacklevel=2)
    return _to_bytes(url)


def _to_bytes(url):
    """to_bytes(u"URL") --> 'URL'."""
    # Most URL schemes require ASCII. If that changes, the conversion
    # can be relaxed.
    # XXX get rid of to_bytes()
    if isinstance(url, str):
        try:
            url = url.encode("ASCII").decode()
        except UnicodeError:
            raise UnicodeError("URL " + repr(url) +
                               " contains non-ASCII characters")
    return url
