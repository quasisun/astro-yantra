
import io
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import streamlit as st

# ------------------------
# Константы
# ------------------------
COLOR_MAP = {
    'овен':      '#ff0000',  # красный
    'телец':     '#ffc0cb',  # розовый
    'близнецы':  '#00ff00',  # зелёный
    'рак':       '#add8e6',  # светло-голубой
    'лев':       '#800000',  # бордовый
    'дева':      '#00ff00',  # зелёный
    'весы':      '#ffc0cb',  # розовый
    'скорпион':  '#ff0000',  # красный
    'стрелец':   '#ffff00',  # жёлтый
    'козерог':   '#0000ff',  # синий
    'водолей':   '#0000ff',  # синий
    'рыбы':      '#ffff00',  # жёлтый
}

# Система координат: 1-3 слева-направо, 1-3 снизу-вверх
PLANET_POSITIONS = {
    'sun':     (2, 2),  # Солнце
    'mercury': (1, 3),  # Меркурий
    'venus':   (2, 3),  # Венера
    'moon':    (3, 3),  # Луна
    'jupiter': (1, 2),  # Юпитер
    'mars':    (3, 2),  # Марс
    'ketu':    (1, 1),  # Кету
    'saturn':  (2, 1),  # Сатурн
    'rahu':    (3, 1),  # Раху
}

PLANET_LABELS_RU = {
    'sun': 'Солнце',
    'moon': 'Луна',
    'mercury': 'Меркурий',
    'venus': 'Венера',
    'mars': 'Марс',
    'jupiter': 'Юпитер',
    'saturn': 'Сатурн',
    'rahu': 'Раху',
    'ketu': 'Кету',
}

ZODIAC_SIGNS = [
    'Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева',
    'Весы', 'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы',
]


# ------------------------
# Функции
# ------------------------
def get_color(sign: str) -> str:
    """Вернуть цвет для знака (строка в нижнем регистре)."""
    return COLOR_MAP.get(sign.lower(), '#ffffff')  # по умолчанию — белый


def overlay_navagraha_grid(img: Image.Image, planet_signs: dict[str, str], alpha: float = 0.45):
    """Создаёт matplotlib-фигуру с наложенной сеткой и заливками."""
    width, height = img.size
    cell_w, cell_h = width / 3, height / 3

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(img)
    ax.axis('off')

    for planet, (x_idx, y_idx) in PLANET_POSITIONS.items():
        sign = planet_signs.get(planet)
        if not sign:
            continue  # знак не указан — пропускаем

        # матплотлибу нужны координаты от левого-верхнего угла,
        # ось y идёт сверху вниз, поэтому переворачиваем y-индекс
        rect_x = (x_idx - 1) * cell_w
        rect_y = (3 - y_idx) * cell_h

        color = get_color(sign)
        rect = patches.Rectangle(
            (rect_x, rect_y),
            cell_w, cell_h,
            linewidth=0,
            facecolor=color,
            alpha=alpha,
        )
        ax.add_patch(rect)

        # подпись по центру
        ax.text(
            rect_x + cell_w / 2,
            rect_y + cell_h / 2,
            PLANET_LABELS_RU[planet],
            color='white',
            fontsize=12,
            ha='center',
            va='center',
            weight='bold',
        )

    plt.tight_layout()
    return fig


# ------------------------
# Streamlit UI
# ------------------------
st.set_page_config(page_title='Navagraha Yantra Overlay', layout='centered')
st.title('Навграха янтра — раскраска секторов')

# Боковая панель с настройками
with st.sidebar:
    st.header('Настройки')
    alpha = st.slider('Прозрачность заливки', 0.1, 1.0, 0.45, 0.05)
    uploaded = st.file_uploader('Загрузите изображение янтры (PNG / JPG)', type=['png', 'jpg', 'jpeg'])

# Загружаем изображение
if uploaded is not None:
    image = Image.open(uploaded).convert('RGBA')
else:
    # Изображение по умолчанию (должно лежать рядом со скриптом)
    try:
        image = Image.open('navagraha_yantra.png').convert('RGBA')
    except FileNotFoundError:
        st.error('По умолчанию файл navagraha_yantra.png не найден. Загрузите изображение вручную!')
        st.stop()

st.subheader('Укажите знак зодиака для каждой планеты:')

# Форма выбора знаков
def zodiac_select(label_key):
    return st.selectbox(
        PLANET_LABELS_RU[label_key],
        options=ZODIAC_SIGNS,
        key=label_key,
    )

with st.form('sign_form'):
    cols = st.columns(3)
    user_signs = {}
    # расположим планеты в читаемом порядке
    order = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'rahu', 'ketu']
    for idx, planet in enumerate(order):
        with cols[idx % 3]:
            sign = zodiac_select(planet)
            user_signs[planet] = sign
    submitted = st.form_submit_button('Показать янтру')

if submitted:
    fig = overlay_navagraha_grid(image, user_signs, alpha=alpha)
    st.pyplot(fig)

    # Кнопка скачивания PNG
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    st.download_button(
        label='Скачать PNG',
        data=buf,
        file_name='navagraha_overlay.png',
        mime='image/png',
    )
    plt.close(fig)
