import os
import json
import random
from datetime import datetime
import anthropic

SITE_THEME = "メダカの飼い方と改良メダカ品種ガイド【初心者〜中級者向け】"

ARTICLE_TOPICS = [
    "メダカ飼育セットのおすすめ5選【初心者が失敗しない選び方】",
    "メダカ水槽の立ち上げ方 バクテリアを増やす完全手順",
    "メダカのビオトープ 初心者向け必要なものと作り方",
    "室内メダカ飼育に必要なもの一覧【最低限の費用まとめ】",
    "メダカを買う前に知っておくべき5つのこと",
    "改良メダカの品種一覧【初心者におすすめ10選と選び方】",
    "三色メダカとは？特徴・値段・飼い方を初心者向けに解説",
    "幹之メダカの種類と体外光の違いをわかりやすく比較",
    "ラメメダカの飼い方と光を綺麗に出すコツ",
    "ダルマメダカの飼い方【体型の特徴と繁殖が難しい理由】",
    "メダカの針子が死ぬ原因と生存率を劇的に上げる3つの方法",
    "メダカの卵の管理方法【孵化までの日数と水温・注意点】",
    "メダカが産卵しない6つの原因と今すぐできる対策",
    "メダカの繁殖サイクルと増やすために必要な環境づくり",
    "メダカの冬越し 屋外飼育で絶対失敗しない方法",
    "メダカの夏対策 水温上昇を防ぐ5つのコツ",
    "メダカ水槽の水換え頻度と正しいやり方【初心者向け】",
    "メダカが次々と死ぬ原因TOP5と今すぐできる対処法",
    "メダカの白点病 症状・原因・治療薬の使い方を解説",
    "メダカがエサを食べない時の原因と対処法",
    "メダカ水槽の水が白く濁る原因と解決策",
    "メダカの産卵床おすすめ5選【卵を効率よく採る方法も解説】",
    "メダカ用フィルターおすすめ5選【水流が弱いものを厳選】",
    "メダカの餌おすすめランキング【稚魚・成魚別に徹底比較】",
    "メダカ屋外飼育容器おすすめ5選【トロ舟・発泡スチロール比較】",
]


def get_used_topics():
    try:
        with open("used_topics.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_used_topic(topic):
    used = get_used_topics()
    used.append(topic)
    with open("used_topics.json", "w", encoding="utf-8") as f:
        json.dump(used, f, ensure_ascii=False, indent=2)


def pick_topic():
    used = get_used_topics()
    remaining = [t for t in ARTICLE_TOPICS if t not in used]
    if not remaining:
        remaining = ARTICLE_TOPICS
        with open("used_topics.json", "w") as f:
            json.dump([], f)
    return random.choice(remaining)


def generate_article(topic):
    print("記事を生成中: " + topic)
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = "あなたはメダカ飼育に詳しいSEOライターです。\n"
    prompt += "テーマ「" + SITE_THEME + "」の記事を書いてください。\n"
    prompt += "タイトル: " + topic + "\n\n"
    prompt += "必ずJSON形式だけで出力してください。他のテキストは不要です。\n"
    prompt += "{\n"
    prompt += '  "title": "タイトルをここに",\n'
    prompt += '  "description": "120文字以内の説明",\n'
    prompt += '  "tags": ["メダカ", "メダカ飼育"],\n'
    prompt += '  "body": "本文をMarkdown形式で1500文字以上"\n'
    prompt += "}"

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    print("APIレスポンス取得完了")

    if raw.startswith("```"):
        lines = raw.split("\n")
        lines = [l for l in lines if not l.startswith("```")]
        raw = "\n".join(lines)

    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("JSONが見つかりません: " + raw[:200])

    json_str = raw[start:end]
    data = json.loads(json_str)
    return data


def create_jekyll_post(article):
    today = datetime.now().strftime("%Y-%m-%d")
    tags_str = ""
    for t in article["tags"]:
        tags_str += "  - " + t + "\n"

    front_matter = "---\n"
    front_matter += "layout: default\n"
    front_matter += 'title: "' + article["title"] + '"\n'
    front_matter += "date: " + today + "\n"
    front_matter += 'description: "' + article["description"] + '"\n'
    front_matter += "tags:\n"
    front_matter += tags_str
    front_matter += "---\n\n"

    affiliate_block = """
---

## 楽天市場でメダカ用品をさがす

<!-- START MoshimoAffiliateEasyLink -->
<script type="text/javascript">
(function(b,c,f,g,a,d,e){b.MoshimoAffiliateObject=a;
b[a]=b[a]||function(){arguments.currentScript=c.currentScript
||c.scripts[c.scripts.length-2];(b[a].q=b[a].q||[]).push(arguments)};
c.getElementById(a)||(d=c.createElement(f),d.src=g,
d.id=a,e=c.getElementsByTagName("body")[0],e.appendChild(d))})
(window,document,"script","//dn.msmstatic.com/site/cardlink/bundle.js?20220329","msmaflink");
msmaflink({"n":"（めだか）（水草）おしゃれにテーブルで楽しむメダカ水槽セット　説明書付　飼育セット　本州四国限定","b":"","t":"","d":"https:\\/\\/thumbnail.image.rakuten.co.jp","c_p":"\\/@0_mall\\/chanet\\/cabinet\\/201","p":["\\/20106-1.jpg","\\/20106-2.jpg","\\/20106-3.jpg"],"u":{"u":"https:\\/\\/item.rakuten.co.jp\\/chanet\\/20106\\/","t":"rakuten","r_v":""},"v":"2.1","b_l":[{"id":1,"u_tx":"楽天市場で見る","u_bc":"#f76956","u_url":"https:\\/\\/item.rakuten.co.jp\\/chanet\\/20106\\/","a_id":5639267,"p_id":54,"pl_id":27059,"pc_id":54,"s_n":"rakuten","u_so":1}],"eid":"198wY","s":"s"});
</script>
<div id="msmaflink-198wY">リンク</div>
<!-- MoshimoAffiliateEasyLink END -->
"""

    return front_matter + article["body"] + affiliate_block


def save_post(content):
    os.makedirs("_posts", exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    slug = "article-" + datetime.now().strftime("%H%M%S")
    filename = "_posts/" + today + "-" + slug + ".md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print("保存完了: " + filename)
    return filename


def main():
    topic = pick_topic()
    article = generate_article(topic)
    post_content = create_jekyll_post(article)
    save_post(post_content)
    save_used_topic(topic)
    print("完了: " + article["title"])


if __name__ == "__main__":
    main()
