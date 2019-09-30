# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestPartials::test_benefits 1'] = '''

<div class="grid-benefits">
    
    
    
    
        <h3 class="grid-benefits__title1">Test title</h3>
    
    
        <h3 class="grid-benefits__title2">Test title</h3>
    
    
        <h3 class="grid-benefits__title3">Test title</h3>
    
    <p class="grid-benefits__text1">Test text</p>
    <p class="grid-benefits__text2">Test text</p>
    <p class="grid-benefits__text3">Test text</p>
    
        <div class="grid-benefits__button1">
            <a href="/" class="button button--regular button--secondary button--secondary--dark">Test button</a>
        </div>
    
    
        <div class="grid-benefits__button2">
            <a href="/" class="button button--regular button--secondary button--secondary--dark">Test button</a>
        </div>
    
    
        <div class="grid-benefits__button3">
            <a href="/" class="button button--regular button--secondary button--secondary--dark">Test button</a>
        </div>
    
</div>
'''

snapshots['TestPartials::test_game_banner 1'] = '''

<div class="row">
    <div class="banner banner--game col-center col-lg-10 col-sm-12 test--class">
        <div>
            <p class="banner--game__text banner--game__ages">Test ages</p>
            <h1 class="banner--game__title">Test title</h1>
            <p class="banner--game__text"><strong>Test description</strong></p>
            <a href="/play/rapid-router/"
               class="button button--big button-primary button--primary--general-educate">Test button</a>
        </div>
    </div>
</div>
'''

snapshots['TestPartials::test_headline 1'] = '''<h1>Test title</h1>
<h4 class="col-sm-6 col-center">Test description</h4>
'''
