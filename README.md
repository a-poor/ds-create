# ds-create

_created by Austin Poor_

A simple CLI program (inspired by _create-react-app_) for creating program templates.

## To Install

```bash
pip install ds-create
```

## To Run

Instructions are formatted as follows:

```bash
ds-create [command] -n [template-name]
```

List of commands:
* `snap`: save a new template
* `create`: extract template contents
* `update`: update template
* `delete`: delete template
* `list`: list templates or list template contents

### List Templates

List all templates:

```bash
ds-create list
```

List info for template `app-template`:

```bash
ds-create list -n app-template
```

### Save a Template

To save the current directory as a new template called `app-template`, run the following:

```bash
ds-create snap -n app-template
```

### Create from Template

Extract the contents of `app-template` in the current directory:

```bash
ds-create create -n app-template
```

### Update from Template

Update the contents of `app-template` in the current directory:

```bash
ds-create update -n app-template
```

### Delete a Template

Delete template `app-template`:

```bash
ds-create delete -n app-template
```

Delete all templates (you'll be prompted for confirmation):

```bash
ds-create delete
```


