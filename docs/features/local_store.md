# 🔐 Store files locally

!!! Example "📝 Basic concepts"

    - store folder: `storage` folder inside your tome home. The default path is `.tome/storage`. 

If you want to store some files in a shared commands, you need a way to store this files in a simple and reproducible way. You can use the standard tome cache folder using the `tome_api.store` API to do it.

```python
import os

from tome.command import tome_command
from tome.api.output import TomeOutput

@tome_command()
def mycommand(tome_api, parser, *args):
    '''Saying hello tome from file.'''
    assets_folder = os.path.join(tome_api.store.folder, 'assets')
    os.makedirs(assets_folder, exist_ok=True)

    with open(os.path.join(assets_folder, 'asset.txt'), 'w') as file:
        file.write("Hello world!")
    with open(os.path.join(assets_folder, 'asset.txt'), 'r') as file:
        TomeOutput().info(file.read())
```