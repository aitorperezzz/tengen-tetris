/* This is the tetromino piece. It begins at the top and moves down. */
class Piece {
	constructor(type) {
		this.squares = [];
		this.center = undefined;

		/* If type is undefined, just create an empty piece. */
		if (type == undefined) {
			return;
		}

		/* Create a different piece depending on the type. */
		let centeri = 0, centerj = 5;
		switch (type) {
			case 'T':
				this.squares.push(new Square(centeri, centerj, true));
				this.squares.push(new Square(centeri, centerj + 1, true));
				this.squares.push(new Square(centeri + 1, centerj, true));
				this.squares.push(new Square(centeri, centerj - 1, true));
				break;
			case 'J':
				this.squares.push(new Square(centeri, centerj, true));
				this.squares.push(new Square(centeri, centerj + 1, true));
				this.squares.push(new Square(centeri + 1, centerj + 1, true));
				this.squares.push(new Square(centeri, centerj - 1, true));
				break;
			case 'Z':
				this.squares.push(new Square(centeri, centerj, true));
				this.squares.push(new Square(centeri + 1, centerj + 1, true));
				this.squares.push(new Square(centeri + 1, centerj, true));
				this.squares.push(new Square(centeri, centerj - 1, true));
				break;
			case 'O':
				this.squares.push(new Square(centeri, centerj, true));
				this.squares.push(new Square(centeri, centerj + 1, true));
				this.squares.push(new Square(centeri + 1, centerj + 1, true));
				this.squares.push(new Square(centeri + 1, centerj, true));
				break;
			case 'S':
				this.squares.push(new Square(centeri, centerj, true));
				this.squares.push(new Square(centeri, centerj + 1, true));
				this.squares.push(new Square(centeri + 1, centerj, true));
				this.squares.push(new Square(centeri + 1, centerj - 1, true));
				break;
			case 'L':
				this.squares.push(new Square(centeri, centerj, true));
				this.squares.push(new Square(centeri, centerj + 1, true));
				this.squares.push(new Square(centeri + 1, centerj - 1, true));
				this.squares.push(new Square(centeri, centerj - 1, true));
				break;
			case 'I':
				this.squares.push(new Square(centeri, centerj, true));
				this.squares.push(new Square(centeri, centerj + 1, true));
				this.squares.push(new Square(centeri, centerj - 1, true));
				this.squares.push(new Square(centeri, centerj - 2, true));
				break;
		}

		/* Point the center piece to the first one. */
		this.center = this.squares[0];
	}

	/* Tries to move the piece in the requested direction. */
	move(direction, grid) {
		let canMove = true;
		for (let k = 0; k < this.squares.length; k++) {
			if (!this.squares[k].canMove(direction, grid)) {
				canMove = false;
				break;
			}
		}

		/* If it cannot move down, let the grid take the piece. */
		if (!canMove) {
			if (direction == DIR_DOWN) {
				grid.receive(this);
			}
			return false;
		}

		/* All the squares can move, so move them. */
		for (let k = 0; k < this.squares.length; k++) {
			this.squares[k].move(direction);
		}

		return true;
	}

	/* Rotates this piece inside the grid givem */
	rotate(grid) {
		/* Create a new piece that is this one rotated. */
		let rotatedPiece = this.createRotatedPiece();
		for (let k = 0; k < rotatedPiece.squares.length; k++) {
			if (!grid.validPosition(rotatedPiece.squares[k].i, rotatedPiece.squares[k].j)) {
				return false;
			}
		}

		/* All the pieces are allowed to rotate, so copy the rotated piece into this one. */
		for (let k = 0; k < this.squares.length; k++) {
			this.squares[k] = rotatedPiece.squares[k];
		}
		this.center = rotatedPiece.center;
	}

	/* Returns a new piece with the squares of this one rotated. */
	createRotatedPiece() {
		let rotatedPiece = new Piece(undefined);
		for (let k = 0; k < this.squares.length; k++) {
			/* Rotate this square. */
			let newSquare = this.squares[k].rotatedFrom(this.center);
			rotatedPiece.squares.push(newSquare);
		}
		rotatedPiece.center = rotatedPiece.squares[0];

		return rotatedPiece;
	}

	/* Displays this piece calling display on each of the squares. */
	display(initialx, initialy, size) {
		for (let i = 0; i < this.squares.length; i++) {
			this.squares[i].display(initialx, initialy, size);
		}
	}
}
