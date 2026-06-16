"""
自動記事生成スクリプト
Claude APIを使って毎週新しい記事を生成し、_posts/ に保存する
"""

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
    "メダカ飼育の初期費用はいくら？最安セット構成を解説",
    "改良メダカの品種一覧【初心者におすすめ10選と選び方】",
    "三色メダカとは？特徴・値段・飼い方を初心者向けに解説",
    "幹之メダカの種類と体外光の違いをわかりやすく比較",
    "ラメメダカの飼い方と光を綺麗に出すコツ",
    "ダルマメダカの飼い方【体型の特徴と繁殖が難しい理由】",
    "マリアージュメダカとは？特徴と入手方法・相場を解説",
    "メダカの針子が死ぬ原因と生存率を劇的に上げる3つの方法",
    "メダカの卵の管理方法【孵化までの日数と水温・注意点】",
    "メダカが産卵しない6つの原因と今すぐできる対策",
    "稚魚と親メダカを分けるタイミングと安全な隔離方法",
    "メダカの繁殖サイクルと増やすために必要な環境づくり",
    "針子の餌は何がいい？種類と与え方・頻度を徹底解説",
    "メダカの冬越し 屋外飼育で絶対失敗しない方法",
    "メダカの夏対策 水温上昇を防ぐ5つのコツと日よけの選び方",
    "春のメダカ飼育 繁殖シーズン前にやること・揃えるもの",
    "メダカの屋外飼育 月別管理カレンダー",
    "メダカ水槽の水換え頻度と正しいやり方【初心者向け】",
    "メダカが次々と死ぬ原因TOP5と今すぐできる対処法",
    "メダカの白点病 症状・原因・治療薬の使い方を解説",
    "メダカがエサを食べない時の原因と対処法",
    "メダカ水槽の水が白く濁る原因と解決策",
    "メダカがぼーっとしている・元気がない時のチェックリスト",
    "メダカの産卵床おすすめ5選【卵を効率よく採る方法も解説】",
    "メダカ用フィルターおすすめ5選【水流が弱いものを厳選】",
    "メダカの餌おすすめランキング【稚魚・成魚別に徹底比較】",
    "メダカ屋外飼育容器おすすめ5選【トロ舟・発泡スチロール比較】",
    "メダカ水槽に入れる水草おすすめ5選【産卵・水質改善効果も】",
]

ADSENSE_CODE = """
<!-- Google AdSense -->
<!-- 審査通過後にここにAdSenseコードを貼り付けてください -->
"""

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


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
    print(f"記事を生成中: {topic}")
    prompt = f"""あなたはメダカ飼育に詳しいSEOライターです。
「{SITE_THEME}」の読者向けに記事を書いてください。

タイトル: {topic}

以下のJSON形式のみで出力してください（前置き不要）:
{{
  "title": "記事タイトル",
  "description": "120文字以内のメタディスクリプション",
  "tags": ["メダカ", "メダカ飼育", "改良メダカ"],
  "body": "本文（Markdown形式・1800文字以上）"
}}

本文の構成:
## この記事でわかること
## メインコンテンツ（h2見出し2〜3個）
## よくある質問
## まとめ"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1
    data = json.loads(raw[start:end])
    return data


def create_jekyll_post(article):
    today = datetime.now().strftime("%Y-%m-%d")
    tags_str = "\n".join([f"  - {t}" for t in article["tags"]])
    front_matter = f"""---
layout: default
title: "{article['title']}"
date: {today}
description: "{article['description']}"
tags:
{tags_str}
---

"""
    body = article["body"]
    paragraphs = body.split("\n\n")
    mid = len(paragraphs) // 2
    paragraphs.insert(mid, ADSENSE_CODE)
    body_with_ads = "\n\n".join(paragraphs)
    return front_matter + body_with_ads


def save_post(content, title):
    os.makedirs("_posts", exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    slug = f"article-{datetime.now().strftime('%H%M%S')}"
    filename = f"_posts/{today}-{slug}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"保存完了: {filename}")
    return filename


def main():
    topic = pick_topic()
    article = generate_article(topic)
    post_content = create_jekyll_post(article)
    save_post(post_content, article["title"])
    save_used_topic(topic)
    print(f"完了！ '{article['title']}' を公開準備しました")


if __name__ == "__main__":
    main()
