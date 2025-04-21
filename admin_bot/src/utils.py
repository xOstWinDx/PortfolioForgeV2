from aiogram.types import MessageEntity


def entities_to_html(text: str, entities: list[MessageEntity] = None) -> str:  # type: ignore
    if not entities or not text:
        return text or ""

    entities = sorted(entities, key=lambda e: (e.offset, -e.length))
    result = []
    stack = []
    i = 0

    while i < len(text):
        while entities and entities[0].offset == i:
            entity = entities.pop(0)
            stack.append((entity, i + entity.length))

        while stack and stack[-1][1] <= i:
            entity, _ = stack.pop()
            if entity.type == "bold":
                result.append("</b>")
            elif entity.type == "italic":
                result.append("</i>")
            elif entity.type == "underline":
                result.append("</u>")
            elif entity.type == "text_link":
                result.append("</a>")
            elif entity.type == "url":
                result.append("</a>")
            elif entity.type == "code":
                result.append("</code>")
            elif entity.type == "pre":
                result.append("</pre>")

        for entity, end_pos in stack:
            if entity.offset == i:
                if entity.type == "bold":
                    result.append("<b>")
                elif entity.type == "italic":
                    result.append("<i>")
                elif entity.type == "underline":
                    result.append("<u>")
                elif entity.type == "text_link":
                    result.append(f'<a href="{entity.url}">')
                elif entity.type == "url":
                    fragment = text[entity.offset : entity.offset + entity.length]
                    result.append(f'<a href="{fragment}">')
                elif entity.type == "code":
                    result.append("<code>")
                elif entity.type == "pre":
                    result.append("<pre>")

        if not stack or i < stack[-1][1]:
            result.append(text[i])
        i += 1

    while stack:
        entity, _ = stack.pop()
        if entity.type == "bold":
            result.append("</b>")
        elif entity.type == "italic":
            result.append("</i>")
        elif entity.type == "underline":
            result.append("</u>")
        elif entity.type == "text_link":
            result.append("</a>")
        elif entity.type == "url":
            result.append("</a>")
        elif entity.type == "code":
            result.append("</code>")
        elif entity.type == "pre":
            result.append("</pre>")

    return "".join(result)
