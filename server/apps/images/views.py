import redis
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from settings.components.common import REDIS_HOST, REDIS_PORT, REDIS_DB
from .forms import ImageCreateForm
from .models import Image
from ..actions.utils import create_action

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


@login_required
def image_create(request):
    if request.method == 'POST':
        # форма отправлена
        form = ImageCreateForm(data=request.POST)

        if form.is_valid():
            # данные в форме валидны
            cd = form.cleaned_data
            new_image = form.save(commit=False)

            # назначить текущего пользователя элементу
            new_image.user = request.user
            new_image.save()
            create_action(request.user, 'bookmarked image', new_image)
            messages.success(request, 'Image created')
            # перенаправить к представлению детальной информации о только что созданном элементе
            return redirect(new_image.get_absolute_url())

    else:
        # скомпоновать форму с данными предоставленными букмарклетом методом GET
        form = ImageCreateForm(data=request.GET)

    return render(request, 'images/image/create.html',
                  context={
                      'section': 'images',
                      'form': form,
                  })


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    # увеличить общее число просмотров изображения на 1
    total_views = r.incrby(f"image:{image.id}:views")
    # увеличить рейтинг изобажения на 1
    r.zincrby(f"image_ranking", 1, image.id)
    return render(request, 'images/image/detail.html',
                  context={
                      'section': 'images',
                      'image': image,
                      'total_views': total_views,
                  })


@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')  # "like" or "unlike"

    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)

            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass

    return JsonResponse({'status': 'error'})


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page', 1)
    images_only = request.GET.get('images_only')

    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом, то доставить первую страницу
        images = paginator.page(1)

    except EmptyPage:
        if images_only:
            # Если AJAX-запрос и страница вне диапазона, то вернуть пустую страницу
            return HttpResponse('')
        
        # Если страница вне диапазона, то вернуть последнюю страницу результатов
        images = paginator.page(paginator.num_pages)

    if images_only:
        return render(request, 'images/image/list_images.html',
                      context={
                          'section': 'images',
                          'images': images,
                      })

    return render(request, 'images/image/list.html',
                  context={
                      'section': 'images',
                      'images': images,
                  })

@login_required
def image_ranking(request):
    # получить словарь рейтинга изображений
    image_ranking_lst = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking_lst]

    # получить наиболее просматриваемые изображения
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(request, 'images/image/ranking.html',
                  context={
                      'section': 'images',
                      'most_viewed': most_viewed,
                  })

