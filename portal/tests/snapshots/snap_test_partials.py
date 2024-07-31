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
