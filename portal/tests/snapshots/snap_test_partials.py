# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots[
    "test_banner 1"
] = """<div class="banner banner--teacher row">
    <div class="col-sm-5 col-sm-offset-2">
        <h1 class="banner__text--primary">Test title</h1>
        
            <h4>Test subtitle</h4>
        
        
            <p>Test text</p>
        
    </div>
    <div class="col-sm-5">
        <div class="banner--picture"><div class="banner--picture__inside1"><div class="banner--picture__inside2 test--image--class"></div></div></div>
    </div>
</div>
"""

snapshots[
    "test_headline 1"
] = """<h1>Test title</h1>
<h6 class="col-sm-6 col-center">Test description</h6>
"""

snapshots[
    "test_benefits 1"
] = """

<div class="grid-benefits row col-sm-10 col-lg-8 col-center">
    
    
    
    
        <h3 class="grid-benefits__title grid-benefits__title1">Test title</h3>
    
    
        <h3 class="grid-benefits__title grid-benefits__title2">Test title</h3>
    
    
        <h3 class="grid-benefits__title grid-benefits__title3">Test title</h3>
    
    <p class="grid-benefits__text1">Test text</p>
    <p class="grid-benefits__text2">Test text</p>
    <p class="grid-benefits__text3">Test text</p>
    
        <div class="grid-benefits__button grid-benefits__button1">
            <a href="/" class="button button--regular button--secondary button--secondary--dark">Test button</a>
        </div>
    
    
        <div class="grid-benefits__button grid-benefits__button2">
            <a href="/" class="button button--regular button--secondary button--secondary--dark">Test button</a>
        </div>
    
    
        <div class="grid-benefits__button grid-benefits__button3">
            <a href="/" class="button button--regular button--secondary button--secondary--dark">Test button</a>
        </div>
    
</div>
"""

snapshots[
    "test_game_banner 1"
] = """

<div class="banner--game col-center col-lg-10 col-sm-12 test--class">
    <div>
        <h4 class="banner--game__text banner--game__ages">Test ages</h4>
        <h1 class="banner--game__title">Test title</h1>
        <p class="banner--game__text"><strong>Test description</strong></p>
        <a href="/play/"
           class="button button--big button-primary button--primary--general-educate">Test button</a>
    </div>
</div>
"""
