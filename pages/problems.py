from pages.page import CollectionEditorPage

class ProblemsPage(CollectionEditorPage):

    def __init__(self, collection=None):

        fields = {
            'language': {
                'type': 'dropdown',
                'label': 'Language',
                'options': ["python", "cpp"],
                'on_change': self.render_markdown,
            },
            'submission': {
                'type': 'textedit',
                'label': 'Submission',
                'on_change': self.render_markdown,
            },
        }

        intended_collections = ['problems']

        super().__init__(collection=collection, fields=fields, intended_collections=intended_collections, theme='github-dark', title="Problems")
    
    def gen_html(self):
        return r"""
            <!DOCTYPE html>
            <html>
                <head>
                    <meta charset="utf-8" />
                    <style>
                        body {
                            tab-size: 4;
                            font-family: 'Fira Code', monospace;
                        }
                    </style>
                </head>

                <body>
                    <div id="content"></div>

                    <script type="module">

                        import { createHighlighter } from 'https://esm.sh/shiki@3.0.0'; // or esm.run

                        let highlighter = null;

                        async function initShiki(theme) {
                            highlighter = await createHighlighter({
                                themes: [theme],
                                langs: ["python", "javascript", "cpp", "java", "html"]
                            });
                        }

                        window.renderCode = async function (code, language = "python", theme = "%s") {
                            if (!highlighter) await initShiki(theme);

                            const html = highlighter.codeToHtml(code, {
                                lang: language,
                                theme: theme
                            });

                            const container = document.getElementById("content");
                            container.innerHTML = html;
                        };
                    </script>
                </body>
            </html>

        """ % (
            self.theme,
        )
    
    def render_markdown(self):
        code_lang = self.field_widgets['language'].currentText().strip()
        code_str = self.field_widgets['submission'].toPlainText()
        js = f"renderCode({code_str!r}, {code_lang!r}, '{self.theme}');"
        self.web.page().runJavaScript(js)


class USACOProblemsPage(CollectionEditorPage):

    def __init__(self, collection=None):

        fields = {
            'link': {
                'type': 'lineedit',
                'label': 'Problem Link',
                'collection': ['usaco'],
            },
            'division': {
                'type': 'dropdown',
                'label': 'Division',
                'options': ["Bronze", "Silver", "Gold", "Platinum"],
                'collection': ['usaco'],
            },
            'title': {
                'type': 'lineedit',
                'label': 'Title',
                'collection': ['usaco', None], # None = take from this collection
            },
            'language': {
                'type': 'dropdown',
                'label': 'Language',
                'options': ["python", "cpp"],
                'on_change': self.render_markdown,
            },
            'submission': {
                'type': 'textedit',
                'label': 'Submission',
                'on_change': self.render_markdown,
            },
        }

        tag = 'usaco'

        intended_collections = ['problems']

        super().__init__(collection=collection, fields=fields, tag=tag, intended_collections=intended_collections, theme='github-dark', title="USACO Problems")
    
    def gen_html(self):
        return r"""
            <!DOCTYPE html>
            <html>
                <head>
                    <meta charset="utf-8" />
                    <style>
                        body {
                            tab-size: 4;
                            font-family: 'Fira Code', monospace;
                        }
                    </style>
                </head>

                <body>
                    <div id="content"></div>

                    <script type="module">

                        import { createHighlighter } from 'https://esm.sh/shiki@3.0.0'; // or esm.run

                        let highlighter = null;

                        async function initShiki(theme) {
                            highlighter = await createHighlighter({
                                themes: [theme],
                                langs: ["python", "javascript", "cpp", "java", "html"]
                            });
                        }

                        window.renderCode = async function (code, language = "python", theme = "%s") {
                            if (!highlighter) await initShiki(theme);

                            const html = highlighter.codeToHtml(code, {
                                lang: language,
                                theme: theme
                            });

                            const container = document.getElementById("content");
                            container.innerHTML = html;
                        };
                    </script>
                </body>
            </html>

        """ % (
            self.theme,
        )
    
    def render_markdown(self):
        if not hasattr(self, "htmlLoaded") or not self.htmlLoaded:
            return
        code_lang = self.field_widgets['language'].currentText().strip()
        code_str = self.field_widgets['submission'].toPlainText()
        js = f"renderCode({code_str!r}, {code_lang!r}, '{self.theme}');"
        self.web.page().runJavaScript(js)

