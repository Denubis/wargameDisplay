def generate_chyron_html(chyron_data, turn, policies=None):
    chyron_html = f'<a href="/?turn={turn+1}"><div id="breaking">TURN {turn}</div></a>'
    chyron_html += '<div id="newsTicker"><p>'
    for item in chyron_data:
        print(item)
        chyron_html += '<span class="story">'
        if "source" in item:            
            chyron_html += f'"{item["text"]}"'
        else:
            chyron_html += f'{item["text"]}'
        if "source" in item:
            chyron_html += f' ({item["source"]})'
        chyron_html += "</span>"
        chyron_html += '<span>+++ </span>'
    chyron_html += "</p></div>"
    return chyron_html
