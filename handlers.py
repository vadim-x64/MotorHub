import logging
from aiogram import Bot, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_categories, get_cars_by_category, get_car_images
from utils import get_message

async def show_categories(message: Message, pool):
    categories = await get_categories(pool)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=cat["name"], callback_data=f"category_{cat['id']}_0_0")]
            for cat in categories
        ]
    )
    await message.answer(get_message("categories_message"), reply_markup=keyboard)

async def show_cars(callback: types.CallbackQuery, pool, bot: Bot):
    user_name = callback.from_user.full_name
    user_id = callback.from_user.id
    logging.info(f"Користувач {user_name} (ID: {user_id}) натиснув кнопку {callback.data}")
    parts = callback.data.split('_')
    category_id = int(parts[1])
    car_index = int(parts[2]) if len(parts) > 2 else 0
    photo_index = int(parts[3]) if len(parts) > 3 else 0
    cars = await get_cars_by_category(pool, category_id)

    if not cars:
        await callback.answer("Наразі ця категорія порожня 😕", show_alert=True)
        return

    current_car = cars[car_index]
    images = await get_car_images(pool, current_car["id"])
    buttons = []

    if images:
        photo_buttons = [
            InlineKeyboardButton(
                text="<" if photo_index > 0 else " ",
                callback_data=f"category_{category_id}_{car_index}_{photo_index - 1}" if photo_index > 0 else "ignore"
            ),
            InlineKeyboardButton(
                text=f"📷 {photo_index + 1}/{len(images)}",
                callback_data="ignore"
            ),
            InlineKeyboardButton(
                text=">" if photo_index < len(images) - 1 else " ",
                callback_data=f"category_{category_id}_{car_index}_{photo_index + 1}" if photo_index < len(
                    images) - 1 else "ignore"
            )
        ]
        buttons.append(photo_buttons)

    car_buttons = []

    if car_index > 0:
        car_buttons.append(InlineKeyboardButton(
            text="Назад",
            callback_data=f"category_{category_id}_{car_index - 1}_0"
        ))
    if car_index < len(cars) - 1:
        car_buttons.append(InlineKeyboardButton(
            text="Вперед",
            callback_data=f"category_{category_id}_{car_index + 1}_0"
        ))

    buttons.append(car_buttons)
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    caption = f"{current_car['name']}\n\n{current_car['description']}\n\nАвто {car_index + 1} з {len(cars)}"

    if images:
        media = types.InputMediaPhoto(
            media=images[photo_index]["image"],
            caption=caption
        )
        if callback.message.photo:
            await callback.message.edit_media(
                media=media,
                reply_markup=keyboard
            )
        else:
            await bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=images[photo_index]["image"],
                caption=caption,
                reply_markup=keyboard
            )
            await callback.message.delete()
    else:
        if callback.message.photo:
            await callback.message.delete()
            await bot.send_message(
                chat_id=callback.message.chat.id,
                text=caption,
                reply_markup=keyboard
            )
        else:
            await callback.message.edit_text(
                text=caption,
                reply_markup=keyboard
            )
    await callback.answer()