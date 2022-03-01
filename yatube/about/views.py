from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_text'] = 'Об авторе проекта'
        context['body_text_h1'] = 'Привет, я автор'
        context['body_text_p'] = ('Тут я размещу информацию о себе используя '
                                  'свои умения верстать. '
                                  'Картинки, блоки, элементы бустрап. '
                                  'А может быть, просто напишу '
                                  'несколько абзацев текста.')
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_text'] = 'Вот что я люблю! Парапапапа!'
        context['text_li_upper'] = 'Питон королевский, самец'
        context['text_li_lower'] = 'Джанго освобожденный'
        context['aside_p_text'] = 'Технолоджи'
        return context


class AboutUsView(TemplateView):
    template_name = 'about/us.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_text'] = 'О сайте Yatube'
        return context
