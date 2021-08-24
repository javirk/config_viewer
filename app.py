from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_wtf import FlaskForm
from wtforms import Form, FieldList, FormField, StringField
from wtforms import validators
from utils.common_utils import read_config
import os
import random

# Initialize app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sosecret'


def validate_filename():
    message = 'File must exist'

    def _validate_filename(form, field):
        if not os.path.exists(field.data) and field.data != '':
            raise validators.ValidationError(message)

    return _validate_filename

class FileForm(FlaskForm):
    folder_name = StringField('Folder')
    file_name = StringField('Filename', validators=[validate_filename()])


class MainForm(FlaskForm):
    """Parent form."""
    files = FieldList(
        FormField(FileForm),
        min_entries=1,
        max_entries=20
    )


class File:
    def __init__(self, id, file_path):
        self.folder = '/'.join(file_path.split('/')[:-1])
        self.short_folder = file_path.split('/')[-2] + '/' + file_path.split('/')[-1]
        self.name = file_path.split('/')[-1]
        self.path = file_path
        self.data = read_config(file_path)
        self.id = id


class Files:
    def __init__(self):
        self.files = []

    def append(self, file_path):
        for f in self.files:
            if file_path == f.path:
                return
        self.files.append(File(len(self.files), file_path))

    def __getitem__(self, item):
        return self.files[item]

    def delete(self, item):
        if len(self.files) == 1:
            self.files = []
            return

        for f in self.files:
            if f.id == item:
                break
        try:
            self.files.remove(f)
        except UnboundLocalError:
            pass

    def sort(self):
        self.files = sorted(self.files, key=lambda x: x.folder)
        for i, file in enumerate(self.files):
            file.id = i

all_files = Files()
show_files = Files()

@app.route('/', methods=['GET', 'POST'])
def index():
    # form = MainForm()
    form = FileForm(prefix='files-_-')

    if form.validate_on_submit():
        folder_name = form.folder_name.data
        file_name = form.file_name.data  # TODO: Use the filename field
        if folder_name is not None:
            # TODO: Improve with Gonzalo's suggestion
            for root, dirs, files in os.walk(folder_name):
                for file in files:
                    if file.endswith('.yml'):
                        all_files.append(os.path.join(root, file))

    all_files.sort()

    return render_template(
        'index.html',
        form=form,
        files=all_files,
        show_files=show_files
    )

@app.route('/show/<file_id>', methods=['GET'])
def show_file(file_id):
    """Show the details of a file."""
    file = all_files[int(file_id)]

    return render_template(
        'show.html',
        file=file
    )


@app.route('/add', methods=['GET', 'POST'])
def add_file():
    file_id = request.args.get('file_id')
    show_files.append(all_files[int(file_id)].path)
    return jsonify(all_files[int(file_id)].data)


@app.route('/', methods=['GET'])
def add_file_old():
    file_id = request.args.get('file_id', default=1, type=int)
    print('hola!')
    form = MainForm()
    template_form = FileForm(prefix='files-_-')
    show_files.append(all_files[int(file_id)].path)
    # app.route('/')  # This is probably horrible and there are better ways, but I don't know them

    return render_template(
        'index.html',
        form=form,
        files=all_files,
        show_files=show_files,
        _template=template_form
    )

if __name__ == '__main__':
    app.run(debug=True)