def generate_chyron_html(chyron_data, turn):
    chyron_html = f'<div id="breaking">TURN {turn}</div>'
    chyron_html += '<div id="newsTicker"><p>'
    for item in chyron_data:
        print(item)
        chyron_html += '<span class="story">'
        chyron_html += f'{item["text"]}'
        if "source" in item:
            chyron_html += f' ({item["source"]})'
        chyron_html += "</span>"
        chyron_html += '<span> +++ </span>'
    chyron_html += "</p></div>"
    return chyron_html
