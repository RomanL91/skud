function table(socketAddress, trFillFunc) {
  
    // Первоначальное заполнение
    let tableData = JSON.parse(
      document.getElementById("initial_data").textContent
    );
    tableData = tableData?.length ? tableData : [];
  
    let currentPage = 1;
    let rowsPerPage = 100;
    let totalPages = Math.ceil(tableData.length / rowsPerPage);
  
    const paginationContainer = document.querySelector(".pagination");
  
  /**
   * Рендерим таблицу, заполняя строки с помощью переданной функции
   */
  const renderTable = () => {
    const tableBody = document.querySelector("tbody");
    while (tableBody.firstChild) {
      tableBody.removeChild(tableBody.firstChild);
    }
    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const paginatedData = tableData.slice().reverse().slice(start, end);

    paginatedData.forEach((row) => {
      tableBody.append(trFillFunc(row));
    });
  };

  /**
   * Рендерим пагинацию для таблицы
   */
  const renderPagination = () => {
    const clearPagination = () => {
      /** Удаляем и очищаем лисенеры старой пагинации */
      while (paginationContainer.firstChild) {
        paginationContainer.removeChild(paginationContainer.firstChild);
      }
    };

    /** Добавляем кнопку перехода на следующую страницу */
    const addFirstButton = () => {
      const firstButton = document.createElement("button");
      firstButton.textContent = "<<";
      firstButton.disabled = currentPage === 1;
      firstButton.addEventListener("click", () => {
        currentPage = 1;
        renderTable();
        renderPagination();
      });
      paginationContainer.appendChild(firstButton);
    };

    /** Добавляем кнопку перехода на предыдущую страницу */
    const addPrevButton = () => {
      const prevButton = document.createElement("button");
      prevButton.textContent = "<";
      prevButton.disabled = currentPage === 1;
      prevButton.addEventListener("click", () => {
        currentPage -= 1;
        renderTable();
        renderPagination();
      });
      paginationContainer.appendChild(prevButton);
    };

    /** Добавляем кнопку перехода на номер страницы и скрытие страниц, если их слишком много */
    const addPages = () => {
      // Добавляем кнопку перехода на номер страницы
      let startPage = 1;
      let endPage = totalPages;
      if (totalPages > 5) {
        if (currentPage < 4) {
          endPage = 5;
        } else if (currentPage > totalPages - 3) {
          startPage = totalPages - 4;
        } else {
          startPage = currentPage - 2;
          endPage = currentPage + 2;
        }
      }
      for (let i = startPage; i <= endPage; i++) {
        const pageButton = document.createElement("button");
        pageButton.textContent = i;
        pageButton.disabled = i === currentPage;
        pageButton.addEventListener("click", () => {
          currentPage = i;
          renderTable();
          renderPagination();
        });
        paginationContainer.appendChild(pageButton);
      }

      // Добавляем логику перехода на скрытые номера страниц, если больше 5 страниц
      if (totalPages > 5) {
        if (currentPage > 3) {
          const prevPagesButton = document.createElement("button");
          prevPagesButton.textContent = "...";
          prevPagesButton.addEventListener("click", () => {
            currentPage = startPage - 1;
            renderTable();
            renderPagination();
          });
          paginationContainer.insertBefore(
            prevPagesButton,
            paginationContainer.childNodes[2]
          );
        }
        if (currentPage < totalPages - 2) {
          const nextPagesButton = document.createElement("button");
          nextPagesButton.textContent = "...";
          nextPagesButton.addEventListener("click", () => {
            currentPage = endPage + 1;
            renderTable();
            renderPagination();
          });
          paginationContainer.appendChild(nextPagesButton);
        }
      }
    };

    /**Добавляем кнопку перехода на следующую страницу */
    const addNextButton = () => {
      const nextButton = document.createElement("button");
      nextButton.textContent = ">";
      nextButton.disabled = currentPage === totalPages;
      nextButton.addEventListener("click", () => {
        currentPage += 1;
        renderTable();
        renderPagination();
      });
      paginationContainer.appendChild(nextButton);
    };

    /**Добавляем кнопку перехода на последнюю страницу */
    const addLastButton = () => {
      const lastButton = document.createElement("button");
      lastButton.textContent = ">>";
      lastButton.disabled = currentPage === totalPages;
      lastButton.addEventListener("click", () => {
        currentPage = totalPages;
        renderTable();
        renderPagination();
      });
      paginationContainer.appendChild(lastButton);
    };
    clearPagination();
    addFirstButton();
    addPrevButton();
    addPages();
    addNextButton();
    addLastButton();
  };

  /** Устанавливаем связь по сокету */
  const connect = () => {
    let ws = new WebSocket(socketAddress);
    //При получении сообщения
    ws.addEventListener("message", (event) => {
      const newData = JSON.parse(event.data);
      tableData.push(newData);
      totalPages = Math.ceil(tableData.length / rowsPerPage);
      if (currentPage > totalPages) {
        currentPage = totalPages;
      }
      renderTable();
      renderPagination();
    });

    // При потере коннекта
    ws.addEventListener("close", function (event) {
      console.log(
        "Socket is closed. Reconnect will be attempted in 1 second.",
        event.reason
      );
      setTimeout(function () {
        connect();
      }, 1000);
    });
  };



  renderTable();
  renderPagination();
  connect();
}
