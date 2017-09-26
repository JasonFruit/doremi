import strutils, sequtils, parseutils, drmcommon

proc tokenize*(s: string): seq[Token] =
  var cur: Token = newToken()
  var inString = false
  result = newSeq[Token](0)
  for pos in 0..high(s):
    if inString:
      cur.content = cur.content & $s[pos]

      if s[pos] == quote and s[pos-1] != '\\':
        cur.length = pos - cur.start + 1
        result.add(cur)
        cur = newToken(pos + 1)
        inString = false

    elif delimiters.contains(s[pos]):
      if assigners.contains(s[pos]) or brackets.contains(s[pos]) or tripletBrackets.contains(s[pos]):
        if cur.content != "":
          cur.length = pos - cur.start
          result.add(cur)
          cur = newToken(pos)
        cur.content = $s[pos]
        cur.length = pos - cur.start
        result.add(cur)
        cur = newToken(pos + 1)
      else:
        if cur.content == "":
          cur.start = pos + 1
        else:
          cur.length = pos - cur.start
          result.add(cur)
          cur = newToken(pos + 1)
    else:
      if s[pos] == quote:
        inString = true
      cur.content = cur.content & $s[pos]

proc showTokens*(tokens: seq[Token]) =
  for tkn in tokens: 
    echo tkn.content, ": ", tkn.start, ",", tkn.length
