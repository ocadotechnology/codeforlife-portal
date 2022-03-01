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

snapshots['test_card_list 1'] = '''


<script type="text/javascript" src="/static/portal/js/carouselCards.js"></script>

<div id="carouselCards" class="carousel carousel-cards slide" data-ride="carousel" data-interval="false">
    <div class="carousel-inner" role="listbox">
        
            <div class="item col-xs-4 active">
                <div class="card">
                    <div class="card__images">
                        <img class="card__image" src="https://storage.googleapis.com/codeforlife-assets/images/worksheets/future2.jpg">
                    </div>
                    <div class="card__text">
                        <h5 class="card__title">Test card 1</h5>
                        
                            <p>Test description 1</p>
                        
                    </div>
                </div>
            </div>
        
            <div class="item col-xs-4 ">
                <div class="card">
                    <div class="card__images">
                        <img class="card__image" src="https://storage.googleapis.com/codeforlife-assets/images/worksheets/ancient.jpg">
                    </div>
                    <div class="card__text">
                        <h5 class="card__title">Test card 2</h5>
                        
                            <p>Test description 2</p>
                        
                    </div>
                </div>
            </div>
        
            <div class="item col-xs-4 ">
                <div class="card">
                    <div class="card__images">
                        <img class="card__image" src="https://storage.googleapis.com/codeforlife-assets/images/worksheets/modern_day.jpg">
                    </div>
                    <div class="card__text">
                        <h5 class="card__title">Test card 3</h5>
                        
                            <p>Test description 3</p>
                        
                    </div>
                </div>
            </div>
        
            <div class="item col-xs-4 ">
                <div class="card">
                    <div class="card__images">
                        <img class="card__image" src="https://storage.googleapis.com/codeforlife-assets/images/worksheets/prehistory.jpg">
                    </div>
                    <div class="card__text">
                        <h5 class="card__title">Test card 4</h5>
                        
                            <p>Test description 4</p>
                        
                    </div>
                </div>
            </div>
        
            <div class="item col-xs-4 ">
                <div class="card">
                    <div class="card__images">
                        <img class="card__image" src="https://storage.googleapis.com/codeforlife-assets/images/worksheets/broken_future.jpg">
                    </div>
                    <div class="card__text">
                        <h5 class="card__title">Test card 5</h5>
                        
                            <p>Test description 5</p>
                        
                    </div>
                </div>
            </div>
        
    </div>

    <div class="carousel-nav text-center">
        <a class="button prev disabled" data-target="#carouselCards" data-slide="prev">
            <span class="iconify" data-icon="mdi:chevron-left" aria-hidden="true"></span>
            <span class="sr-only">Previous</span>
        </a>
        <a class="button next" data-target="#carouselCards" data-slide="next">
            <span class="iconify" data-icon="mdi:chevron-right" aria-hidden="true"></span>
            <span class="sr-only">Next</span>
        </a>
    </div>
</div>

<script>
    setUpCarouselCards(5)
</script>
'''

snapshots['test_character_list 1'] = '''


<div class="grid grid-characters grid__fit">
    
        <div>
            <img class="grid-character-image" src="https://storage.googleapis.com/codeforlife-assets/images/aimmo_characters/Xian.png">
            <h5 class="grid-character-title">Xian</h5>
            <p>Fun, active, will dance to just about anything that produces a beat. Has great memory, always a joke at hand, might try to introduce memes in Ancient Greece. Scored gold in a track race once and will take any opportunity to bring that up.</p>
        </div>
    
        <div>
            <img class="grid-character-image" src="https://storage.googleapis.com/codeforlife-assets/images/aimmo_characters/Jools.png">
            <h5 class="grid-character-title">Jools</h5>
            <p>A quick-witted kid who wasn’t expecting to embark in a time-warping journey but can’t say no to a challenge. Someone has to keep the rest of the group in check, after all!</p>
        </div>
    
        <div>
            <img class="grid-character-image" src="https://storage.googleapis.com/codeforlife-assets/images/aimmo_characters/Zayed.png">
            <h5 class="grid-character-title">Zayed</h5>
            <p>A pretty chill, curious soul that prefers practice to theory. Always ready to jump into an adventure if it looks interesting enough; not so much otherwise. Probably the one who accidentally turned the time machine on in first place.</p>
        </div>
    
</div>
'''

snapshots['test_headline 1'] = '''<section>
    <h4>Test title</h4>
</section>
<p class="container">Test description</p>
'''

snapshots['test_hero_card 1'] = '''


<div class="card activated-card">
    <div class="activated-text">Activated</div>
    <img class="card__image" src="https://storage.googleapis.com/codeforlife-assets/images/worksheets/future_active.png">
    <div class="card__text">
        <h4 class="card__title">Test title</h4>
        <p>Test description</p>
        <div class="button-group button-group__icon">
            <a target="_blank" href="https://www.codeforlife.education" class="button button--secondary button--secondary--dark button--icon">
                Test button 1<span class="iconify" data-icon="mdi:open-in-new"></span>
            </a>
            <a href="/kurono/play/1/" class="button button--primary button-right-arrow">
                Test button 2
            </a>
        </div>
    </div>
</div>
'''
