from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .forms import ImageCreateForm
from .models import Image


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
    return render(request, 'images/image/detail.html',
                  context={
                      'section': 'images',
                      'image': image,
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
