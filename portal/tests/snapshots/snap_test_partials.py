# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_banner 1'] = '''<div class="banner banner--teacher">
    <div class="container">
        <div class="row">
            <div class="col-sm-12 d-flex">
                <div>
                    <h1 class="banner__text--primary">Test title</h1>
                    
                        <h4>Test subtitle</h4>
                    
                    
                        <p>Test text</p>
                    
                    <div class="button-group">
                        
                        
                    </div>
                </div>
                <div>
                    <div class="banner--picture">
                        <div class="banner--picture__inside1">
                            <div class="banner--picture__inside2 test--image--class"
                                 
                                 >
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
'''

snapshots['test_benefits 1'] = '''

<div class="grid-benefits col-sm-8 col-center">
    
    
    
    
        <h5 class="grid-benefits__title grid-benefits__title1">Test title</h5>
    
    
        <h5 class="grid-benefits__title grid-benefits__title2">Test title</h5>
    
    
        <h5 class="grid-benefits__title grid-benefits__title3">Test title</h5>
    
    <p class="grid-benefits__text1">Test text</p>
    <p class="grid-benefits__text2">Test text</p>
    <p class="grid-benefits__text3">Test text</p>
    
        <div class="grid-benefits__button grid-benefits__button1">
        
            <a href="/" class="button button--secondary button--secondary--dark">Test button</a>
        
        </div>
    
    
        <div class="grid-benefits__button grid-benefits__button2">
        
            <a href="/" class="button button--secondary button--secondary--dark">Test button</a>
        
        </div>
    
    
        <div class="grid-benefits__button grid-benefits__button3">
        
            <a href="/" class="button button--secondary button--secondary--dark">Test button</a>
        
        </div>
    
</div>
'''

snapshots['test_headline 1'] = '''<section>
    <h4>Test title</h4>
</section>
<p class="container">Test description</p>
'''
