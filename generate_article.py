"""
自動記事生成スクリプト
Claude APIを使って毎週新しい記事を生成し、_posts/ に保存する
"""

import os
import json
import random
from datetime import datetime
import anthropic

# ============================================================
# ✏️  ここをカスタマイズしてください
# ============================================================

SITE_THEME = "メダカの飼い方と改良メダカ品種ガイド【初心者〜中級者向け】"

ARTICLE_TOPICS = [
    # ━━ 🔰 初心者導入（購入直結・高CVR） ━━
    "メダカ飼育セットのおすすめ5選【初心者が失敗しない選び方】",
    "メダカ水槽の立ち上げ方 バクテリアを増やす完全手順",
    "メダカのビオトープ 初心者向け必要なものと作り方",
    "室内メダカ飼育に必要なもの一覧【最低限の費用まとめ】",
    "メダカを買う前に知っておくべき5つのこと",
    "メダカ飼育の初期費用はいくら？最安セット構成を解説",

    # ━━ 🐟 品種解説（コレクター層・高単価商品に誘導） ━━
    "改良メダカの品種一覧【初心者におすすめ10選と選び方】",
    "三色メダカとは？特徴・値段・飼い方を初心者向けに解説",
    "幹之メダカの種類と体外光の違いをわかりやすく比較",
    "ラメメダカの飼い方と光を綺麗に出すコツ",
    "ダルマメダカの飼い方【体型の特徴と繁殖が難しい理由】",
    "マリアージュメダカとは？特徴と入手方法・相場を解説",

    # ━━ 🍼 稚魚・繁殖（悩み系・緊急検索でCVR最高） ━━
    "メダカの針子が死ぬ原因と生存率を劇的に上げる3つの方法",
    "メダカの卵の管理方法【孵化までの日数と水温・注意点】",
    "メダカが産卵しない6つの原因と今すぐできる対策",
    "稚魚と親メダカを分けるタイミングと安全な隔離方法",
    "メダカの繁殖サイクルと増やすために必要な環境づくり",
    "針子の餌は何がいい？種類と与え方・頻度を徹底解説",

    # ━━ 🌡️ 季節・管理（季節検索で年間定期流入） ━━
    "メダカの冬越し 屋外飼育で絶対失敗しない方法【水温・容器】",
    "メダカの夏対策 水温上昇を防ぐ5つのコツと日よけの選び方",
    "春のメダカ飼育 繁殖シーズン前にやること・揃えるもの",
    "メダカの屋外飼育 月別管理カレンダー【春夏秋冬まとめ】",
    "メダカ水槽の水換え頻度と正しいやり方【初心者向け】",

    # ━━ 🏥 病気・トラブル（緊急検索・購買に直結） ━━
    "メダカが次々と死ぬ原因TOP5と今すぐできる対処法",
    "メダカの白点病 症状・原因・治療薬の使い方を解説",
    "メダカがエサを食べない時の原因と対処法【季節別】",
    "メダカ水槽の水が白く濁る原因と解決策【立ち上げ直後も】",
    "メダカがぼーっとしている・元気がない時のチェックリスト",

    # ━━ 🛒 商品レビュー（Amazon直結・高収益） ━━
    "メダカの産卵床おすすめ5選【卵を効率よく採る方法も解説】",
    "メダカ用フィルターおすすめ5選【水流が弱いものを厳選】",
    "メダカの餌おすすめランキング【稚魚・成魚別に徹底比較】",
    "メダカ屋外飼育容器おすすめ5選【トロ舟・発泡スチロール比較】",
    "メダカ水槽に入れる水草おすすめ5選【産卵・水質改善効果も】",
]
    "メダカの塩浴のやり方 濃度と期間の正しい知識",

    # 🌿 水草・レイアウト（Amazon購入に直結）
    "メダカ水槽におすすめの水草5選 初心者向け",
    "メダカと相性の良いタンクメイト エビ・貝の選び方",
    "メダカ水槽のレイアウト おしゃれに見せる配置のコツ",
    "産卵床の種類と選び方 自作 vs 市販どちらがいい？",
    "メダカのエサ比較 おすすめ餌と与え方のポイント",
]

ADSENSE_CODE = """
<!-- Google AdSense -->
<!-- ⚠️ 審査通過後にここにAdSenseコードを貼り付けてください -->
"""

# ============================================================

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def get_used_topics():
    """使用済みトピックを記録ファイルから読み込む"""
    try:
        with open("used_topics.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_used_topic(topic):
    """使用済みトピックを記録"""
    used = get_used_topics()
    used.append(topic)
    with open("used_topics.json", "w", encoding="utf-8") as f:
        json.dump(used, f, ensure_ascii=False, indent=2)


def pick_topic():
    """未使用のトピックをランダムに選ぶ"""
    used = get_used_topics()
    remaining = [t for t in ARTICLE_TOPICS if t not in used]

    if not remaining:
        # 全部使ったらリセット
        remaining = ARTICLE_TOPICS
        with open("used_topics.json", "w") as f:
            json.dump([], f)

    return random.choice(remaining)


def generate_article(topic: str) -> dict:
    """Claude APIで記事を生成"""
    print(f"📝 記事を生成中: {topic}")

    prompt = f"""
あなたはメダカ飼育に詳しいSEOライターです。
「{SITE_THEME}」の読者（メダカ初心者〜中級者）向けに記事を書いてください。

タイトル: {topic}

以下のJSON形式のみで出力してください（前置き・バッククォート不要）:
{{
  "title": "記事タイトル",
  "description": "120文字以内のメタディスクリプション（キーワードを自然に含める）",
  "tags": ["メダカ", "メダカ飼育", "改良メダカ", "その他関連タグ1〜2個"],
  "body": "本文（Markdown形式・1800〜2200文字）"
}}

【本文の必須構成】
## この記事でわかること（箇条書き3点）
## [メインH2見出し1]
## [メインH2見出し2]
## [メインH2見出し3]
## よくある質問（Q&A形式で2〜3問）
## まとめ

【SEOルール】
- タイトルのキーワードを冒頭100文字以内に自然に入れる
- 具体的な数字・水温・日数・値段の目安を必ず含める
- 「〜がおすすめです」「〜を選びましょう」など購買を自然に促す表現を使う
- Amazonで買える商品カテゴリ（水槽・フィルター・産卵床・餌など）を具体的に言及する
- 読者の「失敗したくない」「損したくない」感情に寄り添った文体
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()
    # JSONのみ抽出
    start = raw.find("{")
    end = raw.rfind("}") + 1
    data = json.loads(raw[start:end])
    return data


def create_jekyll_post(article: dict) -> str:
    """Jekyll用のMarkdownファイルを生成"""
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

    # AdSenseを本文の途中に挿入
    body = article["body"]
    paragraphs = body.split("\n\n")
    mid = len(paragraphs) // 2
    paragraphs.insert(mid, ADSENSE_CODE)
    body_with_ads = "\n\n".join(paragraphs)

    return front_matter + body_with_ads


def save_post(content: str, title: str):
    """_posts/フォルダに保存"""
    os.makedirs("_posts", exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    # ファイル名用にタイトルを変換
    slug = f"article-{datetime.now().strftime('%H%M%S')}"
    filename = f"_posts/{today}-{slug}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ 保存完了: {filename}")
    return filename


def main():
    topic = pick_topic()
    article = generate_article(topic)
    post_content = create_jekyll_post(article)
    filename = save_post(post_content, article["title"])
    save_used_topic(topic)
    print(f"🎉 完了！ '{article['title']}' を公開準備しました")


if __name__ == "__main__":
    main()
