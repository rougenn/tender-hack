import React, { useState } from 'react';

const UrlChecker = () => {
    const [urls, setUrls] = useState(['']); // Начальное состояние с одним пустым полем
    const [responses, setResponses] = useState([]);
    const [errorMessage, setErrorMessage] = useState('');

    const handleChange = (index, event) => {
        const newUrls = [...urls];
        newUrls[index] = event.target.value; // Обновляем значение конкретного поля
        setUrls(newUrls);
    };

    const handleAddField = () => {
        setUrls([...urls, '']); // Добавляем новое пустое поле
    };

    const handleCheckAndSubmit = async () => {
        const urlPattern = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([\/\w .-]*)*\/?$/;

        const validUrls = urls.filter(url => urlPattern.test(url)); // Фильтруем действительные ссылки

        if (validUrls.length === 0) {
            setErrorMessage('Нет действительных ссылок для отправки.'); // Устанавливаем сообщение об ошибке
            setResponses([]); // Очищаем предыдущие ответы
            return; // Прерываем выполнение функции
        }

        setErrorMessage(''); // Очищаем сообщение об ошибке, если есть действительные ссылки

        try {
            const res = await fetch('http://localhost:5000/api', { // Указываем локальный адрес
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ urls: validUrls }), // Отправляем массив действительных ссылок
            });

            const data = await res.json();
            setResponses(data); // Предполагаем, что сервер возвращает данные
        } catch (error) {
            console.error('Ошибка при отправке запроса:', error);
            setResponses({ error: 'Ошибка при отправке запроса' });
        }
    };

    return (
        <div>
            {urls.map((url, index) => (
                <div key={index}>
                    <input
                        type="text"
                        value={url}
                        onChange={(event) => handleChange(index, event)}
                        placeholder="Введите ссылку"
                    />
                </div>
            ))}
            <button onClick={handleAddField}>Добавить поле ввода</button>
            <button onClick={handleCheckAndSubmit}>проверить и отправить</button>
            {errorMessage && <p>{errorMessage}</p>} {/* Отображаем сообщение об ошибке */}
            {responses && (
                <div>
                    <h3>Ответ от сервера:</h3>
                    <pre>{JSON.stringify(responses, null, 2)}</pre>
                </div>
            )}
        </div>
    );
};

export default UrlChecker;
